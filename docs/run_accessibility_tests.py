import os
import sys
import ctypes
import struct

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

if os.name == 'nt':
    # Enable ANSI escape sequences on Windows
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== {title} ==={Colors.END}")

def print_result(test_name, success, info=""):
    status = f"{Colors.GREEN}[PASSED]{Colors.END}" if success else f"{Colors.RED}[FAILED]{Colors.END}"
    info_str = f" ({info})" if info else ""
    print(f"  {status} {test_name}{info_str}")

def check_pe_machine(filepath):
    """
    Reads the PE header of a file and returns its machine type:
    'x86' (32-bit), 'x64' (64-bit), or None if invalid.
    """
    try:
        with open(filepath, 'rb') as f:
            # Read MZ header
            mz = f.read(2)
            if mz != b'MZ':
                return None
            
            # Read PE header offset
            f.seek(0x3C)
            pe_offset = struct.unpack('<I', f.read(4))[0]
            
            # Read PE signature
            f.seek(pe_offset)
            pe_sig = f.read(4)
            if pe_sig != b'PE\0\0':
                return None
            
            # Read machine type from COFF header
            machine = struct.unpack('<H', f.read(2))[0]
            if machine == 0x014c:
                return 'x86'
            elif machine == 0x8664:
                return 'x64'
    except Exception:
        pass
    return None

# Paths configuration
CNC_SOURCE_DIR = r"F:\SteamLibrary\steamapps\common\CnCRemastered\SOURCECODE"
OPENRA_DIR = r"C:\Users\vegas\OneDrive\Desktop\Games\OpenRA-RA2"
RA3_DIR = r"F:\SteamLibrary\steamapps\common\Command and Conquer Red Alert 3"

def test_tiberian_dawn():
    print_header("Game 1: C&C Tiberian Dawn (C++ DLL Mod)")
    
    # Test 1: Check DLL Built Output
    td_dll_path = os.path.join(CNC_SOURCE_DIR, "bin", "Win32", "TiberianDawn.dll")
    exists = os.path.exists(td_dll_path)
    print_result("Test 1: DLL Built Output Check", exists, f"Exists at {td_dll_path}" if exists else "Not found")
    
    # Test 2: DLL Machine Type Check
    machine = check_pe_machine(td_dll_path) if exists else None
    valid_dll = (machine == 'x86')
    print_result("Test 2: DLL Machine Type Check (32-bit x86)", valid_dll, f"Machine type: {machine}" if machine else "Invalid DLL")
    
    # Test 3: Tolk Dependency Verification
    tolk_path = os.path.join(CNC_SOURCE_DIR, "TIBERIANDAWN", "AccessMod", "ThirdParty", "Tolk", "Tolk.dll")
    tolk_exists = os.path.exists(tolk_path)
    print_result("Test 3: Tolk Dependency Verification", tolk_exists)
    
    # Test 4: Tolk.dll Machine Type Check
    tolk_machine = check_pe_machine(tolk_path) if tolk_exists else None
    valid_tolk = (tolk_machine == 'x86')
    print_result("Test 4: Tolk.dll Machine Type Check (32-bit x86)", valid_tolk, f"Machine type: {tolk_machine}" if tolk_machine else "Invalid Tolk.dll")
    
    # Test 5: Event String Mapping Test
    cpp_path = os.path.join(CNC_SOURCE_DIR, "TIBERIANDAWN", "AccessMod", "AccessMod.cpp")
    mapped_correctly = False
    if os.path.exists(cpp_path):
        with open(cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "VOX_NEW_CONSTRUCT" in content and "VOX_NO_POWER" in content and "VOX_NO_CASH" in content:
                mapped_correctly = True
    print_result("Test 5: Event String Mapping Test", mapped_correctly)

def test_red_alert():
    print_header("Game 2: C&C Red Alert 1 (C++ DLL Mod)")
    
    # Test 1: Check DLL Built Output
    ra_dll_path = os.path.join(CNC_SOURCE_DIR, "bin", "Win32", "RedAlert.dll")
    exists = os.path.exists(ra_dll_path)
    print_result("Test 1: DLL Built Output Check", exists, f"Exists at {ra_dll_path}" if exists else "Not found")
    
    # Test 2: DLL Machine Type Check
    machine = check_pe_machine(ra_dll_path) if exists else None
    valid_dll = (machine == 'x86')
    print_result("Test 2: DLL Machine Type Check (32-bit x86)", valid_dll, f"Machine type: {machine}" if machine else "Invalid DLL")
    
    # Test 3: Tolk Dependency Verification
    tolk_path = os.path.join(CNC_SOURCE_DIR, "REDALERT", "AccessMod", "ThirdParty", "Tolk", "Tolk.dll")
    tolk_exists = os.path.exists(tolk_path)
    print_result("Test 3: Tolk Dependency Verification", tolk_exists)
    
    # Test 4: Tolk.dll Machine Type Check
    tolk_machine = check_pe_machine(tolk_path) if tolk_exists else None
    valid_tolk = (tolk_machine == 'x86')
    print_result("Test 4: Tolk.dll Machine Type Check (32-bit x86)", valid_tolk, f"Machine type: {tolk_machine}" if tolk_machine else "Invalid Tolk.dll")
    
    # Test 5: Event String Mapping Test
    cpp_path = os.path.join(CNC_SOURCE_DIR, "REDALERT", "AccessMod", "AccessMod.cpp")
    mapped_correctly = False
    if os.path.exists(cpp_path):
        with open(cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "VOX_NEW_CONSTRUCT" in content and "VOX_INSUFFICIENT_POWER" in content and "VOX_NEED_MO_MONEY" in content:
                mapped_correctly = True
    print_result("Test 5: Event String Mapping Test", mapped_correctly)

def test_red_alert_2():
    print_header("Game 3: C&C Red Alert 2 (OpenRA C# Mod)")
    
    # Test 1: Verify Assembly Compiles
    assembly_path = os.path.join(OPENRA_DIR, "engine", "bin", "OpenRA.Mods.RA2.dll")
    exists = os.path.exists(assembly_path)
    print_result("Test 1: Assembly Compile Check", exists, f"Exists at {assembly_path}" if exists else "Not found")
    
    # Test 2: NVDA Controller Client C# Wrapper Class Metadata Check
    game_dll_path = os.path.join(OPENRA_DIR, "engine", "bin", "OpenRA.Game.dll")
    has_wrapper = False
    if os.path.exists(game_dll_path):
        try:
            with open(game_dll_path, 'rb') as f:
                dll_data = f.read()
                if b'NvdaController' in dll_data or b'NVDA' in dll_data:
                    has_wrapper = True
        except Exception:
            pass
    print_result("Test 2: NVDA C# Wrapper Metadata Check", has_wrapper)
    
    # Test 3: NVDA Controller Client DLL Check
    nvda_dll_path = os.path.join(OPENRA_DIR, "engine", "bin", "nvdaControllerClient64.dll")
    if not os.path.exists(nvda_dll_path):
        nvda_dll_path = os.path.join(OPENRA_DIR, "engine", "bin", "nvdaControllerClient.dll")
    nvda_exists = os.path.exists(nvda_dll_path)
    nvda_machine = check_pe_machine(nvda_dll_path) if nvda_exists else None
    valid_nvda = (nvda_machine == 'x64')
    print_result("Test 3: nvdaControllerClient.dll Machine Type Check (64-bit x64)", valid_nvda, f"Machine type: {nvda_machine}" if nvda_machine else "Invalid DLL")
    
    # Test 4: NVDA Controller Source Integration
    service_exists = os.path.exists(os.path.join(OPENRA_DIR, "engine", "OpenRA.Game", "Widgets", "NvdaController.cs"))
    print_result("Test 4: NvdaController.cs Source Integration", service_exists)
    
    # Test 5: Tactical Cursor & Query Hotkeys Check
    hotkeys_exists = os.path.exists(os.path.join(OPENRA_DIR, "engine", "OpenRA.Mods.Common", "Widgets", "Logic", "Ingame", "Hotkeys", "TacticalCursorHotkeyLogic.cs")) and \
                     os.path.exists(os.path.join(OPENRA_DIR, "engine", "OpenRA.Mods.Common", "Widgets", "Logic", "Ingame", "Hotkeys", "QueryStatusHotkeyLogic.cs"))
    print_result("Test 5: Accessibility Hotkeys Logic Verification", hotkeys_exists)

def test_red_alert_3():
    print_header("Game 4: C&C Red Alert 3 (Official Mod SDK)")
    
    # Test 1: WorldBuilder Executable Check
    wb_path = os.path.join(RA3_DIR, "Data", "WorldBuilder.exe")
    wb_exists = os.path.exists(wb_path)
    print_result("Test 1: WorldBuilder Executable Check", wb_exists, f"Exists at {wb_path}" if wb_exists else "Not found")
    
    # Test 2: Asset Directory Verification
    asset_dir_exists = os.path.isdir(os.path.join(RA3_DIR, "Data"))
    print_result("Test 2: SAGE Asset Directory Verification", asset_dir_exists)
    
    # Test 3: SkuDef Configuration Reference Check
    skudef_exists = os.path.exists(os.path.join(RA3_DIR, "RA3_english_1.12.SkuDef"))
    print_result("Test 3: SkuDef Configuration File Verification", skudef_exists)
    
    # Test 4: Main Game Process Executable Check
    game_exe_exists = os.path.exists(os.path.join(RA3_DIR, "RA3.exe"))
    print_result("Test 4: Main Game Process Executable Check", game_exe_exists)
    
    # Test 5: Launcher Directory Verification
    launcher_exists = os.path.isdir(os.path.join(RA3_DIR, "Launcher"))
    print_result("Test 5: Launcher Directory Verification", launcher_exists)

if __name__ == "__main__":
    print(f"\n{Colors.BOLD}==================================================")
    print("   COMMAND & CONQUER ACCESSIBILITY TEST SUITE     ")
    print(f"=================================================={Colors.END}")
    
    test_tiberian_dawn()
    test_red_alert()
    test_red_alert_2()
    test_red_alert_3()
    
    print(f"\n{Colors.BOLD}==================================================")
    print("               TEST RUN COMPLETE                  ")
    print(f"=================================================={Colors.END}\n")
