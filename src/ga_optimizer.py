"""Search J1 green splits at a fixed 120 s cycle."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import random
import tempfile

from benchmark import APPROACHES, BASELINE, CONFIG, DEMANDS, TRAIN_SEED, evaluate, write_program


def mutate(greens, rng):
    donor, receiver = rng.sample(range(4), 2)
    shifted = min(rng.randint(1, 8), greens[donor] - 12)
    child = list(greens)
    child[donor] -= shifted
    child[receiver] += shifted
    return tuple(child)


def fitness(metrics):
    return (metrics["collisions"] + metrics["teleports"],
            metrics["pending_departure"],
            metrics["mean_time_loss_s"] + metrics["mean_depart_delay_s"],
            -metrics["arrived"])


def main():
    rng = random.Random(TRAIN_SEED)
    # The stored 1x demand is heaviest on W2E, so include a west-heavy seed.
    population = [BASELINE, (17, 40, 27, 20), (18, 36, 28, 22),
                  (16, 40, 28, 20), (20, 33, 28, 23), (21, 32, 28, 23)]
    scores = {}
    with tempfile.TemporaryDirectory(prefix="signal-search-") as folder:
        def score(greens):
            program = Path(folder) / ("-".join(map(str, greens)) + ".add.xml")
            write_program(program, greens)
            return evaluate(program, DEMANDS["1x"], TRAIN_SEED)

        with ThreadPoolExecutor(max_workers=3) as pool:
            for generation in range(3):
                fresh = list(dict.fromkeys(greens for greens in population if greens not in scores))
                scores.update(zip(fresh, pool.map(score, fresh)))
                parents = sorted(scores, key=lambda greens: fitness(scores[greens]))[:3]
                best = parents[0]
                print(f"Generation {generation + 1}: {best}, "
                      f"time loss {scores[best]['mean_time_loss_s']} s", flush=True)
                population = parents.copy()
                while len(population) < 6:
                    first, second = rng.sample(parents, 2)
                    child = [(a + b) // 2 for a, b in zip(first, second)]
                    child[0] += sum(BASELINE) - sum(child)
                    population.append(mutate(child, rng))

    write_program(CONFIG / "signal_equal.add.xml", BASELINE)
    write_program(CONFIG / "signal_optimized.add.xml", best)
    print(json.dumps({"approach_order": APPROACHES, "cycle_s": 120, "seed": TRAIN_SEED,
                      "evaluated_candidates": len(scores), "baseline_greens": BASELINE,
                      "optimized_greens": best, "baseline": scores[BASELINE],
                      "optimized": scores[best]}, indent=2))


if __name__ == "__main__":
    main()
