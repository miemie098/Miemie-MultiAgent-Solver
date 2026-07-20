from typing import TypedDict, List, Dict, Any

class GraphState(TypedDict):
    query: str
    paper_context: str

    # 🌟 SOP 状态通道硬性隔离：每个 Agent 只能写自己的通道
    search_output: Dict[str, Any]    # 新增：存放检索到的文献片段
    analyzer_output: Dict[str, Any]
    critic_output: Dict[str, Any]
    compactor_output: Dict[str, Any]
    summary_output: Dict[str, Any]   # 新增：存放中间总结状态

    history_logs: List[Dict[str, Any]]
    compressed_context: str
    correction_count: int
    max_corrections: int
    final_report: str  # 最终收敛输出给前端的报告