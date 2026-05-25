# -*- coding: utf-8 -*-
"""
统计 tripinfo.xml 文件中的实际仿真数据
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import statistics

def analyze_tripinfo(file_path):
    """分析单个 tripinfo 文件"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        waiting_times = []
        durations = []
        vehicle_count = 0
        
        for tripinfo in root.findall('.//tripinfo'):
            vehicle_count += 1
            waiting_time = float(tripinfo.get('waitingTime', 0))
            duration = float(tripinfo.get('duration', 0))
            
            waiting_times.append(waiting_time)
            durations.append(duration)
        
        if waiting_times:
            avg_waiting = statistics.mean(waiting_times)
            max_waiting = max(waiting_times)
            avg_duration = statistics.mean(durations)
            
            return {
                'file': file_path.name,
                'vehicles': vehicle_count,
                'avg_waiting': avg_waiting,
                'max_waiting': max_waiting,
                'avg_duration': avg_duration
            }
        else:
            return None
            
    except Exception as e:
        print(f"❌ 读取失败 {file_path}: {e}")
        return None

def main():
    config_dir = Path('D:\\项目一\\config')
    
    tripinfo_files = list(config_dir.glob('tripinfo*.xml'))
    
    print("=" * 80)
    print("项目一仿真数据统计分析报告")
    print("=" * 80)
    print(f"\n找到 {len(tripinfo_files)} 个 tripinfo 文件\n")
    
    results = []
    for file in tripinfo_files:
        result = analyze_tripinfo(file)
        if result:
            results.append(result)
            print(f"📊 {result['file']}")
            print(f"   车辆数：{result['vehicles']}")
            print(f"   平均等待时间：{result['avg_waiting']:.2f} 秒")
            print(f"   最大等待时间：{result['max_waiting']:.2f} 秒")
            print(f"   平均行程时间：{result['avg_duration']:.2f} 秒\n")
    
    if results:
        print("=" * 80)
        print("📈 数据汇总")
        print("=" * 80)
        
        # 按流量倍数排序
        sorted_results = sorted(results, key=lambda x: x['file'])
        
        for r in sorted_results:
            flow_type = "官方" if "official" in r['file'] else "优化" if "optimized" in r['file'] else "其他"
            multiplier = ""
            if "3x" in r['file']:
                multiplier = " (3 倍流量)"
            elif "high" in r['file']:
                multiplier = " (高流量)"
            
            print(f"\n{flow_type}{multiplier}:")
            print(f"  文件：{r['file']}")
            print(f"  平均延误：{r['avg_waiting']:.2f} 秒/车")
            print(f"  最大延误：{r['max_waiting']:.2f} 秒")
            print(f"  总车辆：{r['vehicles']} 辆")
        
        print("\n" + "=" * 80)
        print("✅ 统计分析完成！")
        print("=" * 80)
    else:
        print("❌ 未找到有效的 tripinfo 数据")

if __name__ == "__main__":
    main()
