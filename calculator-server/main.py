import math
from collections import deque
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter

from calculator import expand_percent
from models import Expression, CalculatorLog

HISTORY_MAX = 1000
# HISTORY (in-memory for now)
history = deque(maxlen=HISTORY_MAX)

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Safe evaluator ----------
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})

history_list = []

@app.post("/calculate")
def calculate(expr: Expression):
    try:
        code = Expression.expand_percent(expr.expr)
        result = aeval(code)
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": expr, "result": "", "error": msg}
        # TODO: Add history
        
        # add to result history
        history_result = {"timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") , "expr": expr.expr , "result": result }
        history_list.append(history_result)
        
        return {"ok": True, "expr": expr, "result": result, "error": ""}
    except Exception as e:
        return {"ok": False, "expr": expr, "error": str(e)}

# TODO GET /hisory
@app.get("/history")
def get_history(limit: int = None) -> list[CalculatorLog]:
    try:
        newest_first = history_list[::-1]               
        result_history_list = []

        if limit is None or limit <= 0:                 
            for i in newest_first:
                result_history_list.append(i)
            return result_history_list
        
        count_added = 0                             
        for i in newest_first:                         
            if count_added >= limit:                  
                break
            else:
                result_history_list.append(i)           
                count_added += 1                        

        return result_history_list                     

    except Exception as e:
        return {"ok": False, "error": str(e)}

# TODO DELETE /history
@app.delete("/history")
def delete_history():
    try:
        history_list.clear()        # clear list
        # use len() if history get cleared or not
        return {"ok": True, "cleared": len(history_list) <= 0}                      # return result
    except Exception as e:
        return {"ok": False,"cleared": len(history_list) <= 0, "error": str(e)}     # return result
