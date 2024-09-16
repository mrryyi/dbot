import traceback

def log_err_local(e: Exception = None) -> None:
    print(f"[dInternal] [ERR] An error occurred1: {e}")
    print(traceback.format_exc())

def log_inf_local(inf_msg: str) -> None:
    print(f"[dInternal] [INF] {inf_msg}")
