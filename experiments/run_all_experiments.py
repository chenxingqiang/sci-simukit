#!/usr/bin/env python3
"""
实验验证综合运行脚本
自动运行所有6个实验并生成综合报告
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

class ExperimentRunner:
    def __init__(self):
        self.experiments = {
            'exp_1_structure': {
                'name': '结构表征实验',
                'script': 'analysis/lattice_params.py',
                'priority': 'high',
                'estimated_time': '3-6个月'
            },
            'exp_2_doping': {
                'name': '掺杂合成实验',
                'script': 'analysis/doping_synthesis.py',
                'priority': 'high',
                'estimated_time': '6-9个月'
            },
            'exp_3_electronic': {
                'name': '电子性质测量',
                'script': 'analysis/electronic_properties.py',
                'priority': 'high',
                'estimated_time': '3-6个月'
            },
            'exp_4_polaron': {
                'name': '极化子转变验证',
                'script': 'analysis/polaron_transition.py',
                'priority': 'medium',
                'estimated_time': '6-9个月'
            },
            'exp_5_synergy': {
                'name': '协同效应定量验证',
                'script': 'analysis/synergy_effects.py',
                'priority': 'medium',
                'estimated_time': '6-9个月'
            },
            'exp_6_optimal': {
                'name': '最优条件验证',
                'script': 'analysis/optimal_conditions.py',
                'priority': 'low',
                'estimated_time': '9-12个月'
            }
        }
        
        self.results = {}
        self.start_time = datetime.now()
        
    def run_experiment(self, exp_id):
        """运行单个实验"""
        print(f"\n{'='*60}")
        print(f"开始运行实验: {self.experiments[exp_id]['name']}")
        print(f"{'='*60}")
        
        exp_dir = f"experiments/{exp_id}"
        script_path = os.path.join(exp_dir, self.experiments[exp_id]['script'])
        
        if not os.path.exists(script_path):
            print(f"警告: 脚本 {script_path} 不存在，跳过此实验")
            return False
            
        try:
            # 切换到实验目录
            original_dir = os.getcwd()
            os.chdir(exp_dir)
            
            # 运行实验脚本
            result = subprocess.run([sys.executable, self.experiments[exp_id]['script']], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ 实验 {exp_id} 运行成功")
                self.results[exp_id] = {
                    'status': 'success',
                    'output': result.stdout,
                    'timestamp': datetime.now().isoformat()
                }
                return True
            else:
                print(f"❌ 实验 {exp_id} 运行失败")
                print(f"错误信息: {result.stderr}")
                self.results[exp_id] = {
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 实验 {exp_id} 超时")
            self.results[exp_id] = {
                'status': 'timeout',
                'timestamp': datetime.now().isoformat()
            }
            return False
        except Exception as e:
            print(f"💥 实验 {exp_id} 出现异常: {e}")
            self.results[exp_id] = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
        finally:
            os.chdir(original_dir)
            
    def run_all_experiments(self):
        """运行所有实验"""
        print("🚀 开始运行所有实验验证")
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 按优先级运行实验
        high_priority = [exp_id for exp_id, info in self.experiments.items() 
                        if info['priority'] == 'high']
        medium_priority = [exp_id for exp_id, info in self.experiments.items() 
                          if info['priority'] == 'medium']
        low_priority = [exp_id for exp_id, info in self.experiments.items() 
                        if info['priority'] == 'low']
        
        all_experiments = high_priority + medium_priority + low_priority
        
        success_count = 0
        for exp_id in all_experiments:
            if self.run_experiment(exp_id):
                success_count += 1
            time.sleep(1)  # 短暂暂停
            
        print(f"\n{'='*60}")
        print(f"实验运行完成!")
        print(f"成功: {success_count}/{len(all_experiments)}")
        print(f"总耗时: {datetime.now() - self.start_time}")
        print(f"{'='*60}")
        
    def generate_summary_report(self):
        """生成综合报告"""
        report = {
            'experiment_summary': {
                'total_experiments': len(self.experiments),
                'successful_experiments': sum(1 for r in self.results.values() if r['status'] == 'success'),
                'failed_experiments': sum(1 for r in self.results.values() if r['status'] == 'failed'),
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_duration': str(datetime.now() - self.start_time)
            },
            'experiment_details': self.results,
            'experiment_info': self.experiments
        }
        
        # 保存报告
        with open('experiments/experiment_summary_report.json', 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # 生成可视化报告
        self.plot_experiment_results()
        
        print(f"\n📊 综合报告已生成: experiments/experiment_summary_report.json")
        
    def plot_experiment_results(self):
        """绘制实验结果可视化"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 实验状态饼图
        status_counts = {}
        for result in self.results.values():
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
        ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
        ax1.set_title('实验运行状态分布')
        
        # 优先级分布
        priority_counts = {}
        for exp_id, info in self.experiments.items():
            priority = info['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
        ax2.bar(priority_counts.keys(), priority_counts.values(), 
               color=['red', 'orange', 'green'])
        ax2.set_title('实验优先级分布')
        ax2.set_ylabel('实验数量')
        
        # 预计时间分布
        time_ranges = [info['estimated_time'] for info in self.experiments.values()]
        time_labels = ['3-6个月', '6-9个月', '9-12个月']
        time_counts = [time_ranges.count(label) for label in time_labels]
        
        ax3.bar(time_labels, time_counts, color=['lightblue', 'lightgreen', 'lightcoral'])
        ax3.set_title('预计完成时间分布')
        ax3.set_ylabel('实验数量')
        ax3.tick_params(axis='x', rotation=45)
        
        # 实验进度时间线
        exp_names = [info['name'] for info in self.experiments.values()]
        y_pos = np.arange(len(exp_names))
        
        colors = []
        for exp_id in self.experiments.keys():
            if exp_id in self.results:
                status = self.results[exp_id]['status']
                if status == 'success':
                    colors.append('green')
                elif status == 'failed':
                    colors.append('red')
                else:
                    colors.append('orange')
            else:
                colors.append('gray')
                
        ax4.barh(y_pos, [1]*len(exp_names), color=colors)
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels(exp_names)
        ax4.set_xlabel('实验状态')
        ax4.set_title('实验进度状态')
        
        plt.tight_layout()
        plt.savefig('experiments/experiment_results_visualization.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_experiment_templates(self):
        """创建实验模板文件"""
        print("📝 创建实验模板文件...")
        
        for exp_id, info in self.experiments.items():
            exp_dir = f"experiments/{exp_id}"
            
            # 创建输入模板
            input_template = {
                "experiment_id": exp_id,
                "experiment_name": info['name'],
                "priority": info['priority'],
                "estimated_time": info['estimated_time'],
                "required_samples": [],
                "required_equipment": [],
                "measurement_parameters": {},
                "expected_results": {},
                "validation_criteria": {}
            }
            
            with open(f"{exp_dir}/inputs/experiment_template.json", 'w') as f:
                json.dump(input_template, f, indent=2, ensure_ascii=False)
                
            # 创建结果模板
            result_template = {
                "experiment_id": exp_id,
                "experiment_name": info['name'],
                "run_date": datetime.now().isoformat(),
                "status": "pending",
                "raw_data": {},
                "processed_data": {},
                "analysis_results": {},
                "validation_results": {},
                "conclusions": {}
            }
            
            with open(f"{exp_dir}/results/result_template.json", 'w') as f:
                json.dump(result_template, f, indent=2, ensure_ascii=False)
                
        print("✅ 实验模板文件创建完成")

def main():
    """主函数"""
    runner = ExperimentRunner()
    
    print("🧪 实验验证系统启动")
    print("="*60)
    
    # 创建实验模板
    runner.create_experiment_templates()
    
    # 运行所有实验
    runner.run_all_experiments()
    
    # 生成综合报告
    runner.generate_summary_report()
    
    print("\n🎉 所有实验验证完成!")
    print("📁 结果保存在 experiments/ 目录下")

if __name__ == "__main__":
    main()
