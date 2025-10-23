#!/usr/bin/env python3
"""
实验2: 掺杂合成实验
合成B/N/P掺杂的qHP C₆₀网络
"""

import numpy as np
import json
import matplotlib.pyplot as plt
import os

class DopingSynthesisAnalyzer:
    def __init__(self, data_dir="outputs"):
        self.data_dir = data_dir
        self.target_concentrations = [2.5, 5.0, 7.5]  # %
        self.dopants = ['B', 'N', 'P']
        self.tolerance = 0.2  # ±0.2%

    def load_xps_data(self, filename):
        """加载XPS数据"""
        filepath = os.path.join(self.data_dir, 'xps', filename)
        data = np.loadtxt(filepath)
        return data[:, 0], data[:, 1]  # binding_energy, intensity

    def load_edx_data(self, filename):
        """加载EDX数据"""
        filepath = os.path.join(self.data_dir, 'edx', filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data

    def analyze_doping_concentration(self, edx_data):
        """分析掺杂浓度"""
        concentrations = {}

        for dopant in self.dopants:
            if dopant in edx_data:
                # 计算原子百分比
                dopant_atoms = edx_data[dopant]['count']
                total_atoms = sum([edx_data[element]['count']
                                for element in edx_data])
                concentration = (dopant_atoms / total_atoms) * 100
                concentrations[dopant] = concentration

        return concentrations

    def analyze_chemical_state(self, xps_data):
        """分析化学状态"""
        chemical_states = {}

        for dopant in self.dopants:
            binding_energy, intensity = xps_data[dopant]

            # 根据结合能确定化学状态
            if dopant == 'B':
                if 187 < binding_energy < 189:
                    chemical_states[dopant] = 'B³⁺'
                else:
                    chemical_states[dopant] = 'Unknown'
            elif dopant == 'N':
                if 397 < binding_energy < 399:
                    chemical_states[dopant] = 'N³⁻'
                else:
                    chemical_states[dopant] = 'Unknown'
            elif dopant == 'P':
                if 132 < binding_energy < 134:
                    chemical_states[dopant] = 'P³⁺'
                else:
                    chemical_states[dopant] = 'Unknown'

        return chemical_states

    def check_doping_uniformity(self, edx_maps):
        """检查掺杂均匀性"""
        uniformity_results = {}

        for dopant in self.dopants:
            if dopant in edx_maps:
                # 计算标准偏差
                concentrations = edx_maps[dopant]['concentrations']
                std_dev = np.std(concentrations)
                mean_conc = np.mean(concentrations)
                cv = (std_dev / mean_conc) * 100  # 变异系数

                uniformity_results[dopant] = {
                    'mean_concentration': mean_conc,
                    'std_deviation': std_dev,
                    'coefficient_of_variation': cv,
                    'uniform': cv < 10  # 变异系数<10%认为均匀
                }

        return uniformity_results

    def validate_synthesis(self, concentrations, chemical_states, uniformity):
        """验证合成结果"""
        validation_results = {
            'concentration_valid': False,
            'chemical_state_valid': False,
            'uniformity_valid': False,
            'overall_valid': False
        }

        # 验证浓度
        concentration_valid = True
        for dopant in self.dopants:
            if dopant in concentrations:
                for target in self.target_concentrations:
                    if abs(concentrations[dopant] - target) <= self.tolerance:
                        break
                else:
                    concentration_valid = False
                    break

        validation_results['concentration_valid'] = concentration_valid

        # 验证化学状态
        expected_states = {'B': 'B³⁺', 'N': 'N³⁻', 'P': 'P³⁺'}
        chemical_state_valid = all(
            chemical_states.get(dopant) == expected_states[dopant]
            for dopant in self.dopants if dopant in chemical_states
        )
        validation_results['chemical_state_valid'] = chemical_state_valid

        # 验证均匀性
        uniformity_valid = all(
            uniformity[dopant]['uniform']
            for dopant in self.dopants if dopant in uniformity
        )
        validation_results['uniformity_valid'] = uniformity_valid

        # 总体验证
        validation_results['overall_valid'] = all([
            concentration_valid, chemical_state_valid, uniformity_valid
        ])

        return validation_results

    def save_results(self, concentrations, chemical_states, uniformity, validation_results):
        """保存分析结果"""
        results = {
            'doping_concentrations': concentrations,
            'chemical_states': chemical_states,
            'uniformity_analysis': uniformity,
            'validation_results': validation_results,
            'target_concentrations': self.target_concentrations,
            'tolerance': self.tolerance
        }

        with open('results/doping_synthesis.json', 'w') as f:
            json.dump(results, f, indent=2)

    def plot_results(self, concentrations, chemical_states, uniformity):
        """绘制分析结果"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

        # 掺杂浓度对比
        dopants = list(concentrations.keys())
        target_concs = [self.target_concentrations[0]] * len(dopants)
        actual_concs = [concentrations[dopant] for dopant in dopants]

        x = np.arange(len(dopants))
        width = 0.35

        ax1.bar(x - width/2, target_concs, width, label='Target', alpha=0.7)
        ax1.bar(x + width/2, actual_concs, width, label='Actual', alpha=0.7)
        ax1.set_xlabel('Dopant')
        ax1.set_ylabel('Concentration (%)')
        ax1.set_title('Doping Concentration Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(dopants)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 化学状态
        states = [chemical_states[dopant] for dopant in dopants]
        ax2.bar(dopants, [1]*len(dopants), color=['red', 'blue', 'green'])
        ax2.set_ylabel('Chemical State')
        ax2.set_title('Chemical States')
        for i, (dopant, state) in enumerate(zip(dopants, states)):
            ax2.text(i, 0.5, state, ha='center', va='center', fontweight='bold')
        ax2.set_ylim(0, 1)

        # 均匀性分析
        cv_values = [uniformity[dopant]['coefficient_of_variation'] for dopant in dopants]
        ax3.bar(dopants, cv_values, color=['orange', 'purple', 'brown'])
        ax3.axhline(y=10, color='red', linestyle='--', label='Threshold (10%)')
        ax3.set_ylabel('Coefficient of Variation (%)')
        ax3.set_title('Doping Uniformity')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # XPS谱图示例
        binding_energy = np.linspace(180, 200, 100)
        intensity = np.exp(-(binding_energy - 188)**2 / 2) + 0.1 * np.random.randn(100)
        ax4.plot(binding_energy, intensity)
        ax4.set_xlabel('Binding Energy (eV)')
        ax4.set_ylabel('Intensity (a.u.)')
        ax4.set_title('XPS Spectrum (B 1s)')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('results/doping_synthesis.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """主函数"""
    analyzer = DopingSynthesisAnalyzer()

    # 模拟数据（实际实验中从文件读取）
    concentrations = {'B': 5.1, 'N': 4.9, 'P': 7.3}
    chemical_states = {'B': 'B³⁺', 'N': 'N³⁻', 'P': 'P³⁺'}
    uniformity = {
        'B': {'mean_concentration': 5.1, 'std_deviation': 0.3,
              'coefficient_of_variation': 5.9, 'uniform': True},
        'N': {'mean_concentration': 4.9, 'std_deviation': 0.4,
              'coefficient_of_variation': 8.2, 'uniform': True},
        'P': {'mean_concentration': 7.3, 'std_deviation': 0.6,
              'coefficient_of_variation': 8.2, 'uniform': True}
    }

    # 验证结果
    validation_results = analyzer.validate_synthesis(
        concentrations, chemical_states, uniformity
    )

    # 保存结果
    analyzer.save_results(concentrations, chemical_states, uniformity, validation_results)

    # 绘制结果
    analyzer.plot_results(concentrations, chemical_states, uniformity)

    print("掺杂合成实验分析完成!")
    print(f"验证结果: {validation_results}")

if __name__ == "__main__":
    main()
