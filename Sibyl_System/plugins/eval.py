import sys
from Sibyl_System import system_cmd, System, INSPECTORS, SIBYL
from io import StringIO
import traceback
import inspect


@System.on(system_cmd(pattern=r"syl (exec|execute|x|ex)"))
async def run(event):
  if event.from_id not in INSPECTORS and not SIBYL:
    return
  code = event.text.split(" ", 2)
  if len(code) == 2:
      return
  stderr, output, wizardry = None, None, None
  code = code[2]
  old_stdout = sys.stdout
  old_stderr = sys.stderr
  redirected_output = sys.stdout = StringIO()
  redirected_error = sys.stderr = StringIO()
  try:
      await async_exec(code, event)
  except Exception:
      wizardry = traceback.format_exc()
  output = redirected_output.getvalue()
  stderr = redirected_error.getvalue()
  sys.stdout = old_stdout
  sys.stderr = old_stderr
  if wizardry:
      final = "**Output**:\n`" + wizardry
  elif output:
      final = "**Output**:\n`" + output
  elif stderr:
      final = "**Output**:\n`" + stderr
  else:
      final = "`OwO no output"
  if len(final) > 4096:
      with open("exec.txt", "w+", encoding="utf-8") as f:
          f.write(final)
      await System.send_file(event.chat_id, "exec.txt")
      return
  await event.reply(f'{final}`')


@System.on(system_cmd(pattern=r"syl (ev|eva|eval|py)"))
async def run_eval(event):
  if event.from_id in INSPECTORS or SIBYL:
    cmd = event.text.split(" ", 2)
    cmd = cmd[2] if len(cmd) > 2 else ""
    try:
        evaluation = eval(cmd)
        if inspect.isawaitable(evaluation):
            evaluation = await evaluation
    except (Exception) as e:
        evaluation = str(e)
    await event.reply(f"Output:\n`{evaluation}`")


async def async_exec(code, event):
  if event.from_id in INSPECTORS or SIBYL:
    exec(("async def __async_exec(event): " + "".join(
        f"\n {l}" for l in code.split("\n"))))
    return await locals()["__async_exec"](event)


__plugin_name__ = "py"

help_plus = """
Run code using **exec** 
CMD - <x or ex or exec or execute> your code here
EXAMPLE - `!syl x print("OWO")`
Run code using **eval**
CMD - <ev or eva or eval or py> your code
EXAMPLE - `!syl eval 1 + 1`
"""
