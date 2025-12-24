from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

frameworks = env.get("PIOFRAMEWORK", [])

if "tremo" in frameworks:
    env.SConscript("framework_tremo.py", exports={"env": env})
else:
    print("ERROR: Unsupported framework:", frameworks)
    env.Exit(1)
