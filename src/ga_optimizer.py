# -*- coding: utf-8 -*-


import traci
import subprocess
import random
import time
from datetime import datetime
import os
import sys

# ==================== 配置参数 ====================
SUMO_BINARY = "sumo-gui"
CONFIG_FILE = "changjiang.sumocfg"
PORT = 8813
TIMEOUT = 30

# 交通灯 ID
TLS_ID = "J1"


PHASES = [
    # 相位 1: 东西直行 (31s)
    ["GGGrrrGGGrrrGGGrrr", 31],
    ["yyyyyyyryyyyyyyry", 3],
    
    # 相位 2: 东西左转 (18s)
    ["lllLLLlllLLLlllLLL", 18],
    ["yyyrrryyyyyyyyyyyy", 3],
    
    # 相位 3: 南北直行 (30s)
    ["rrrGGGrrrGGGrrrGGG", 30],
    ["rrryyyrrryyyrrryyy", 3],
    
    # 相位 4: 南北左转 (11s)
    ["LLLrrrLLLrrrLLLrrr", 11],
    ["yyyrrryyyrrryyyrrr", 3],
]


POPULATION_SIZE = 20
GENERATIONS = 30
MUTATION_RATE = 0.1

# ==================== 工具函数 ====================

def start_sumo():
    """启动 SUMO"""
    try:

        print("[CLEANUP] 清理旧进程...")
        subprocess.run("taskkill /F /IM sumo-gui.exe 2>$null", shell=True)
        subprocess.run("taskkill /F /IM sumo.exe 2>$null", shell=True)
        time.sleep(2)
        

        print("[START] 启动 SUMO...")
        sumo_process = subprocess.Popen([
            SUMO_BINARY,
            "-c", CONFIG_FILE,
            "--start"
        ])
        

        print(f"[WAIT] 等待 SUMO 启动 (最多{TIMEOUT}秒)...")
        for i in range(TIMEOUT):
            try:
                traci.init(PORT, timeout=10)
                print(f"✓ SUMO 启动成功 (尝试{i+1}秒)")
                return sumo_process
            except Exception as e:
                if i < TIMEOUT - 1:
                    print(f"  重试中... ({i+1}/{TIMEOUT})")
                time.sleep(1)
        
        print("✗ SUMO 启动超时")
        raise TimeoutError("无法连接到 SUMO")
        
    except Exception as e:
        print(f"✗ SUMO 启动失败：{e}")
        sys.exit(1)

def get_phase_durations(individual):
    
    durations = []
    idx = 0
    for i in range(0, len(PHASES), 2):
        green_duration = individual[idx]
        durations.append(green_duration)  # 绿灯
        durations.append(3)  # 黄灯
        idx += 1
    return durations

def set_traffic_lights(durations):
    
    phase_durations = []
    for i in range(0, len(PHASES), 2):
        phase_durations.append(durations[i // 2])  # 绿灯
        phase_durations.append(3)  # 黄灯
    
    for i, (phase, _) in enumerate(PHASES):
        traci.trafficlight.setPhase(TLS_ID, i)
        if i % 2 == 0:
            traci.trafficlight.setPhaseDuration(TLS_ID, phase_durations[i])
        else:
            traci.trafficlight.setPhaseDuration(TLS_ID, 3)

def run_simulation(duration=3600):
    
    stats = {
        "arrived": 0,
        "waiting_time": 0,
        "time_loss": 0
    }
    
    step = 0
    while step < duration:
        traci.simulationStep()
        arrived = traci.simulation.getArrivedNumber()
        stats["arrived"] += arrived
        
        waiting_vehicles = traci.vehicle.getIDList()
        for veh in waiting_vehicles:
            speed = traci.vehicle.getSpeed(veh)
            if speed < 0.1:
                stats["waiting_time"] += 1
        
        step += 1
    
    return stats

def evaluate(individual):
    
    try:

        durations = get_phase_durations(individual)
        set_traffic_lights(durations)
        

        stats = run_simulation()
        

        fitness = stats["arrived"]
        
        return fitness
        
    except Exception as e:
        print(f"评估失败：{e}")
        return 0

def create_individual():
    

    return [
        random.randint(25, 40),
        random.randint(15, 25),
        random.randint(20, 35),
        random.randint(10, 20),
    ]

def crossover(parent1, parent2):
    
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(individual):
    
    mutated = individual.copy()
    for i in range(len(mutated)):
        if random.random() < MUTATION_RATE:
            mutated[i] += random.randint(-3, 3)
            mutated[i] = max(10, min(50, mutated[i]))
    return mutated

# ==================== 主程序 ====================

def main():
    print("=" * 60)
    print("合肥长江中路信号优化系统 - 最终完美版")
    print("=" * 60)
    
    # 启动 SUMO
    sumo_proc = start_sumo()
    
    try:

        population = [create_individual() for _ in range(POPULATION_SIZE)]
        
        best_ever_fitness = 0
        best_ever_individual = None
        
        for gen in range(GENERATIONS):
            print(f"\n{'='*50}")
            print(f"第 {gen + 1}/{GENERATIONS} 代")
            print(f"{'='*50}")
            
            # 评估
            fitnesses = []
            for i, ind in enumerate(population):
                fitness = evaluate(ind)
                fitnesses.append((ind, fitness))
                print(f"  个体{i+1}: {ind} -> 通过{fitness}辆车", end='\r')
            
            # 排序
            fitnesses.sort(key=lambda x: x[1], reverse=True)
            
            current_best = fitnesses[0]
            print(f"\n  最佳：{current_best[0]} -> 通过{current_best[1]}辆车")
            
            if current_best[1] > best_ever_fitness:
                best_ever_fitness = current_best[1]
                best_ever_individual = current_best[0]
            
            # 选择
            parents = [f[0] for f in fitnesses[:10]]
            

            children = []
            while len(children) < POPULATION_SIZE - 1:
                p1 = random.choice(parents)
                p2 = random.choice(parents)
                c1, c2 = crossover(p1, p2)
                children.append(mutate(c1))
                if len(children) < POPULATION_SIZE - 1:
                    children.append(mutate(c2))
            
            population = [best_ever_individual] + children
        

        print(f"\n{'='*60}")
        print("优化完成!")
        print(f"{'='*60}")
        print(f"最佳相位时长:")
        print(f"  东西直行：{best_ever_individual[0]}秒")
        print(f"  东西左转：{best_ever_individual[1]}秒")
        print(f"  南北直行：{best_ever_individual[2]}秒")
        print(f"  南北左转：{best_ever_individual[3]}秒")
        print(f"总周期：{sum(best_ever_individual) + 12}秒")
        print(f"最大通过量：{best_ever_fitness}辆车")
        
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        traci.close()
        sumo_proc.terminate()

if __name__ == "__main__":
    main()
