from supabase import ClientOptions
import inspect
print("ClientOptions attributes:")
for name, value in inspect.getmembers(ClientOptions):
    if not name.startswith('__'):
        print(f" - {name}")
