import traceback

def log_exception_local(e: Exception = None) -> None:
    print(f"[dInternal] [ERR] An error occurred1: {e}")
    print(traceback.format_exc())

def log_warn_local(warn_msg: str) -> None:
    print(f"[dInternal] [WARN] {warn_msg}")

def log_inf_local(inf_msg: str) -> None:
    print(f"[dInternal] [INF] {inf_msg}")
