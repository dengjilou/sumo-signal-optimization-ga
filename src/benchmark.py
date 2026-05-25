# -*- coding: utf-8 -*-
"""
终极流量对比测试 - 5 倍和 6 倍流量
使用 static 交通灯，对比官方配时和优化配时
"""

import subprocess
import time
from datetime import datetime
import xml.etree.ElementTree as ET
import os

SIMULATION_TIME = 3600

def run_test(name, net_file, routes_file):
    """运行仿真并返回结果"""
    
    print(f"\n{'='*70}")
    print(f"开始仿真：{name}")
    print(f"{'='*70}")
    
    tripinfo_file = f"d:\\项目一\\config\\trip_{name}_ultimate.xml"
    
    try:
        # 清理
        print("[清理] 清理进程和文件...")
        subprocess.run("taskkill /F /IM sumo.exe 2>$null", shell=True)
        subprocess.run("taskkill /F /IM sumo-gui.exe 2>$null", shell=True)
        time.sleep(3)
        
        if os.path.exists(tripinfo_file):
            try:
                os.remove(tripinfo_file)
            except:
                pass
        
        # 运行 SUMO
        print(f"[运行] {SIMULATION_TIME}秒高流量仿真...")
        result = subprocess.run([
            "sumo",
            "--net-file", net_file,
            "--route-files", routes_file,
            "--begin", "0",
            "--end", str(SIMULATION_TIME),
            "--step-length", "1",
            "--tripinfo-output", tripinfo_file,
            "--no-step-log"
        ], timeout=600)
        
        if result.returncode != 0:
            error_msg = result.stderr[:200] if result.stderr else '未知错误'
            print(f"✗ SUMO 失败：{error_msg}")
            return None, None
        
        print("✓ 仿真完成")
        
        # 解析数据
        print("[分析] 读取 tripinfo...")
        
        if not os.path.exists(tripinfo_file):
            print("✗ tripinfo 未生成")
            return None, None
        
        tree = ET.parse(tripinfo_file)
        root = tree.getroot()
        
        total_waiting = 0.0
        vehicle_count = 0
        
        for tripinfo in root.findall('tripinfo'):
            waiting = float(tripinfo.get('waitingTime', '0'))
            total_waiting += waiting
            vehicle_count += 1
        
        avg_delay = total_waiting / vehicle_count if vehicle_count > 0 else 0
        
        print(f"  ✓ 车辆数：{vehicle_count}")
        print(f"  ✓ 总等待：{total_waiting:.2f}秒")
        print(f"  ✓ 平均延误：{avg_delay:.2f}秒/车")
        
        return avg_delay, vehicle_count
        
    except Exception as e:
        print(f"✗ 失败：{e}")
        import traceback
        traceback.print_exc()
        return None, None
    
    finally:
        time.sleep(3)
        subprocess.run("taskkill /F /IM sumo.exe 2>$null", shell=True)

def test_flow_level(multiplier, flow_file):
    """测试某一流量级别"""
    
    print("\n" + "="*70)
    print(f"【测试 {multiplier}倍流量】")
    print("="*70)
    
    official_net = "d:\\项目一\\config\\changjiang_official.net.xml"
    optimized_net = "d:\\项目一\\config\\changjiang_optimized.net.xml"
    
    # 官方配时
    print(f"\n【第 1 轮】官方配时 ({multiplier}x)")
    delay1, count1 = run_test(f"official_{multiplier}x", official_net, flow_file)
    
    if delay1 is None:
        print(f"\n✗ {multiplier}倍官方配时失败")
        return None, None, None, None, 0
    
    # 等待
    print(f"\n等待 5 秒进行下一轮...")
    time.sleep(5)
    
    # 优化配时
    print(f"\n【第 2 轮】优化配时 ({multiplier}x)")
    delay2, count2 = run_test(f"optimized_{multiplier}x", optimized_net, flow_file)
    
    if delay2 is None:
        print(f"\n✗ {multiplier}倍优化配时失败")
        return delay1, 0, count1, 0, 0  # 返回部分数据
    
    # 计算改进率
    if delay1 > 0:
        improvement = (delay1 - delay2) / delay1 * 100
    else:
        improvement = 0
    
    return delay1, delay2, count1, count2, improvement

def main():
    """主函数"""
    
    print("="*70)
    print("终极流量对比测试 - 5 倍/6 倍流量")
    print("="*70)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"仿真时长：{SIMULATION_TIME} 秒")
    print("="*70)
    
    results = {}
    
    # 测试 5 倍流量
    d1, d2, c1, c2, impr = test_flow_level(5, "d:\\项目一\\config\\routes_5x.rou.xml")
    
    if d1 is not None:
        results['5x'] = {
            'official': d1,
            'optimized': d2,
            'count1': c1,
            'count2': c2,
            'improvement': impr
        }
        
        print(f"\n{'='*70}")
        print(f"【5 倍流量结果】")
        print(f"{'='*70}")
        print(f"官方：{d1:.2f}秒/车 ({c1}辆)")
        print(f"优化：{d2:.2f}秒/车 ({c2}辆)")
        print(f"改进：{impr:.2f}%")
        
        # 如果 5 倍流量延误>10 秒，说明已经饱和，可以停止
        if d1 > 10:
            print(f"\n✓ 5 倍流量已饱和，延误显著！")
        else:
            print(f"\n⚠️ 5 倍流量延误不明显，继续测试 6 倍...")
            
            # 测试 6 倍流量
            time.sleep(5)
            d1, d2, c1, c2, impr = test_flow_level(6, "d:\\项目一\\config\\routes_6x.rou.xml")
            
            if d1 is not None:
                results['6x'] = {
                    'official': d1,
                    'optimized': d2,
                    'count1': c1,
                    'count2': c2,
                    'improvement': impr
                }
                
                print(f"\n{'='*70}")
                print(f"【6 倍流量结果】")
                print(f"{'='*70}")
                print(f"官方：{d1:.2f}秒/车 ({c1}辆)")
                print(f"优化：{d2:.2f}秒/车 ({c2}辆)")
                print(f"改进：{impr:.2f}%")
    
    # 输出最终报告
    print("\n" + "="*70)
    print("🎉 终极测试完成！")
    print("="*70)
    
    for mult, res in results.items():
        print(f"\n【{mult}流量】")
        print(f"  官方配时：{res['official']:.2f}秒/车")
        print(f"  优化配时：{res['optimized']:.2f}秒/车")
        print(f"  改进率：{res['improvement']:.2f}%")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"d:\\项目一\\终极测试结果_{timestamp}.txt"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("终极流量对比测试结果\n")
        f.write("="*70 + "\n\n")
        f.write(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for mult, res in results.items():
            f.write(f"{mult}流量:\n")
            f.write("-"*70 + "\n")
            f.write(f"  官方配时：{res['official']:.2f}秒/车 ({res['count1']}辆)\n")
            f.write(f"  优化配时：{res['optimized']:.2f}秒/车 ({res['count2']}辆)\n")
            f.write(f"  改进率：{res['improvement']:.2f}%\n\n")
        
        f.write("\n结论:\n")
        f.write("-"*70 + "\n")
        if results:
            best_mult = max(results.keys(), key=lambda x: results[x]['official'])
            best_impr = results[best_mult]['improvement']
            f.write(f"在{best_mult}流量下达到饱和，改进率为{best_impr:.2f}%\n")
            if best_impr > 15:
                f.write("✅ 优化方案效果显著！\n")
            elif best_impr > 5:
                f.write("⚠️ 优化方案有一定效果\n")
            else:
                f.write("ℹ️ 优化效果不明显\n")
    
    print(f"\n详细结果：{result_file}")
    print("="*70)
    
    # 打开结果
    subprocess.Popen(["notepad", result_file])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n✗ 失败：{e}")
        import traceback
        traceback.print_exc()
    finally:
        subprocess.run("taskkill /F /IM sumo.exe 2>$null", shell=True)
        subprocess.run("taskkill /F /IM sumo-gui.exe 2>$null", shell=True)
