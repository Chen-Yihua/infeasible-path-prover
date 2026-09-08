# Infeasible Path Prover

以自動機（DFA）表示程式路徑，並用 Z3 / PySMT 證明其不可行性的 Software Model Checking 練習專案。

本專案以 **DFA（決定性有限自動機）** 表示程式的所有執行路徑（trace），並利用 **Z3** / **PySMT** 對每條路徑進行不可行性（infeasibility）證明，證明方法包括：

- **Weakest Precondition + UNSAT Core**：計算路徑的最弱前置條件，若不可滿足，取出 UNSAT core 找出造成路徑不可行的衝突條件與變數。
- **Craig Interpolant**：以路徑條件序列計算 Craig interpolant，並比較迴圈展開前後 interpolant 語意是否等價，藉此判斷迴圈是否可以安全併入路徑。

找到一條不可行路徑後，會將其建構成對應的 DFA，並從原始的「全路徑 DFA」中扣除（`difference`），重複此流程直到差集為空，即完成對所有路徑的不可行性證明。

## 檔案結構

```
automata/
├── core/               # 核心模組（package，供 examples/ 以 from core import ... 引用）
│   ├── dfa_operations.py
│   ├── path_operations.py
│   ├── infeasible_proof.py
│   ├── unsat_core_operations.py
│   └── get_interpolant.py
├── examples/           # 進入點腳本（實驗版本）
│   ├── e1_0820.py
│   ├── interpolant_automata.py
│   ├── infeasibility_automata.py
│   └── test.py
├── tools/              # 與主流程無關的獨立小工具
│   └── cfg-parser.py
└── legacy/             # 已被取代、未被引用的舊版程式碼
    └── get_unsat_core.py
```

### core/ 核心模組

| 檔案 | 說明 |
| --- | --- |
| [core/dfa_operations.py](core/dfa_operations.py) | DFA 的建構（`build_dfa`、`update_dfa`）、繪圖（`draw_dfa`）、邊與符號的轉換 |
| [core/path_operations.py](core/path_operations.py) | 圖搜尋（Dijkstra 最短路徑）、迴圈偵測（DFS）、路徑條件擷取、將迴圈併入路徑 |
| [core/infeasible_proof.py](core/infeasible_proof.py) | 計算路徑的 weakest precondition，並以 Z3 證明路徑是否不可行 |
| [core/unsat_core_operations.py](core/unsat_core_operations.py) | 從 UNSAT 的 solver 結果中擷取 unsat core 與衝突變數，並找出造成不可行的條件 |
| [core/get_interpolant.py](core/get_interpolant.py) | 以 PySMT（MathSAT）計算 Craig interpolant，並比對兩個 interpolant 語意是否相同 |

### examples/ 進入點（實驗版本）

以下皆為以同一個範例程式（`p != 0; n >= 0; ...` 的控制流程）驗證整體流程的獨立腳本，依開發先後排序：

| 檔案 | 說明 |
| --- | --- |
| [examples/e1_0820.py](examples/e1_0820.py) | 最早期的實驗版本，圖搜尋與迴圈偵測邏輯尚未拆分至 `core/path_operations.py` |
| [examples/interpolant_automata.py](examples/interpolant_automata.py) | 僅使用 Craig interpolant 方法的版本 |
| [examples/infeasibility_automata.py](examples/infeasibility_automata.py) | 僅使用 UNSAT core 方法的版本，並使用 `VisualDFA` 顯示自動機 |
| [examples/test.py](examples/test.py) | 目前主要版本，整合 interpolant 與 unsat_core 兩種方法（透過 `method` 參數切換） |

### 其他

| 檔案 | 說明 |
| --- | --- |
| [tools/cfg-parser.py](tools/cfg-parser.py) | 將 S-expression 形式的程式描述解析為 control flow graph 並用 Graphviz 繪圖 |
| [legacy/get_unsat_core.py](legacy/get_unsat_core.py) | `core/unsat_core_operations.py` 的舊版，功能已被取代，目前未被任何腳本引用，僅供參考 |

執行時會由 Graphviz 產生 `dfa`、`dfa.png`、`cfg`、`cfg.png`、`Digraph.gv` 等圖檔，這些屬於產生物，已加入 `.gitignore`，不會被提交進版本控制。

## 安裝

需要 Python 3.8，以及以下套件：

```bash
pip install z3-solver PySMT automata-lib visual-automata graphviz
pysmt-install --msat   # Craig interpolant 需要 MathSAT solver
```

另外需安裝系統的 [Graphviz](https://graphviz.org/download/)，供 `graphviz`套件繪製 DFA / CFG 圖片。

> 目前程式碼中仍有 `from asyncio.windows_events import NULL` 的殘留引用，該模組僅存在於 Windows 平台，故現階段這些腳本僅能在 Windows 環境下執行。

## 使用方式

`core/` 是以 `from core import ...` 被 `examples/` 引用的 package，因此進入點腳本須在**專案根目錄**以 `-m` 方式執行，而不能直接 `python examples/test.py`：

```bash
python -m examples.test
```

執行後會：

1. 建立範例程式對應的完整 DFA（所有路徑）。
2. 反覆尋找最短路徑並嘗試證明其不可行，找到後將對應的迴圈嘗試併入路徑。
3. 為每條不可行路徑建構 DFA 並繪製圖片，再從完整 DFA 中扣除，直到差集為空為止。
