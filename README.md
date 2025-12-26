# 使用说明

## 环境要求
- Python 3.8 或以上

## 目录结构
```text
project/
├── PROBLEM.md
├── README.md
├── generator.py
├── baseline.py
├── evaluator.py
├── solver.py
├── ref_dsu.py
├── data/
├── outputs/
└── reports/
```


---

## 三、使用流程（只需三步）

### ① 生成测试数据（只需一次）

在项目根目录执行：

```bash
python generator.py
```

执行后会生成：

```text
data/
├── case_0001.in
├── case_0002.in
├── ...
└── case_0050.in
```

---

### ② 编写你的 solver

编辑文件：

```text
solver.py
```

你的程序需要：

- 从 **标准输入** 读取一个数据文件
- 对每一个查询操作输出一条路径，或输出 `-1`
- 输出格式必须严格符合题面要求

你可以多次修改并保存该文件。

---

### ③ 运行评测程序（自动完成剩余步骤）

在项目根目录执行：

```bash
python evaluator.py
```

评测程序会自动完成：

1. 若 `outputs/` 中不存在对应输出文件，将自动调用你的 `solver.py`
2. 对每一组数据执行评测
3. 检查输出路径的合法性
4. 根据评分规则计算得分

---

## 四、评测结果说明

### 1️⃣ 各组数据得分

文件：

```text
reports/scores.csv
```

示例内容：

```csv
case,score
case_0001,98
case_0002,104
case_0003,121
...
case_0050,87
```

每一行表示一组数据文件的最终得分，范围 **0–200**。

---

### 2️⃣ 最终平均分

文件：

```text
reports/summary.txt
```

示例内容：

```text
average_score,112
```

该数值即为你的最终成绩。

---

### 3️⃣ 终端输出

评测完成后，终端也会输出最终平均分，例如：

```text
Final Average Score: 112
```

---

## 五、重要注意事项

- **每一组数据的时间限制为 8 秒**  
  超时、运行时错误或输出格式错误，都会导致该组数据得分为 **0**
- 输出证词不合法（数量不对、证词重复、引用已撤销证词、证词之间矛盾等），对应查询得分为 **0**

---

## 六、常见使用方式

### 修改 solver 后重新评测

只需再次运行：

```bash
python evaluator.py
```

评测程序会自动重新调用你的 solver 并更新结果。

---

### 重新生成数据（不常用）

如需重新生成测试数据：

```bash
rm -rf data
python generator.py
```

---

> 你只需要关注 **solver.py** 的实现，其余文件无需修改。