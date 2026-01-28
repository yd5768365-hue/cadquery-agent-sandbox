"""
CAE System Test Script
Demonstrate how to use the CAE platform
"""

import json
import subprocess
import time
from pathlib import Path


def run_command(cmd):
    """Execute shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def test_gmsh():
    """Test Gmsh mesh generation"""
    print("=" * 60)
    print("Test 1: Gmsh Mesh Generation")
    print("=" * 60)
    
    # Create a simple geometry file
    geo_content = """
Point(1) = {0, 0, 0, 1.0};
Point(2) = {1, 0, 0, 1.0};
Point(3) = {1, 1, 0, 1.0};
Point(4) = {0, 1, 0, 1.0};
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};
Line Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};
Physical Surface("surface") = {1};
"""
    
    geo_file = Path("test/input/test.geo")
    geo_file.write_text(geo_content)
    print(f"[OK] Created geometry file: {geo_file}")
    
    # Run in Gmsh container
    cmd = f"docker exec cae_gmsh gmsh /app/input/test.geo -2 -o /app/meshes/test.msh"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        print("[OK] Mesh generation successful")
        mesh_file = Path("test/meshes/test.msh")
        if mesh_file.exists():
            print(f"  Mesh file: {mesh_file}")
            print(f"  File size: {mesh_file.stat().st_size / 1024:.2f} KB")
    else:
        print(f"[FAIL] Mesh generation failed: {stderr}")
    
    print()
    return code == 0


def test_calculix():
    """Test CalculiX simulation"""
    print("=" * 60)
    print("Test 2: CalculiX Simulation")
    print("=" * 60)
    
    # Create simple CalculiX input file
    inp_content = """*HEADING
Simple plate test
*NODE, NSET=Nall
1, 0.0, 0.0, 0.0
2, 1.0, 0.0, 0.0
3, 1.0, 1.0, 0.0
4, 0.0, 1.0, 0.0
*ELEMENT, TYPE=C3D8R, ELSET=Eall
1, 1, 2, 3, 4, 1, 2, 3, 4
*MATERIAL, NAME=STEEL
*ELASTIC
210000, 0.3
*SOLID SECTION, ELSET=Eall, MATERIAL=STEEL
*BOUNDARY
N1, 1, 3, 0
*STEP, NLGEOM
*STATIC
*CLOAD
N2, 2, -1000
*NODE FILE
U
*EL FILE
S, E
*END STEP
"""
    
    inp_file = Path("test/analyses/test.inp")
    inp_file.write_text(inp_content)
    print(f"[OK] Created input file: {inp_file}")
    
    # Run in CalculiX container
    cmd = f"docker exec cae_calculix ccx -i /app/analyses/test"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        print("[OK] Simulation completed")
        frd_file = Path("test/analyses/test.frd")
        if frd_file.exists():
            print(f"  Result file: {frd_file}")
            print(f"  File size: {frd_file.stat().st_size / 1024:.2f} KB")
    else:
        print(f"[FAIL] Simulation failed")
        print(f"  Error: {stderr[:200]}")
    
    print()
    return code == 0


def test_celery():
    """Test Celery task queue"""
    print("=" * 60)
    print("Test 3: Celery Task Queue")
    print("=" * 60)
    
    # Check Celery worker status
    cmd = "docker exec cae_celery_worker celery -A tasks inspect active"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        data = json.loads(stdout)
        print("[OK] Celery Worker is running")
        print(f"  Active tasks: {len(data)}")
    else:
        print("[FAIL] Celery check failed")
    
    # Check registered tasks
    cmd = "docker exec cae_celery_worker celery -A tasks inspect registered"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        tasks = list(json.loads(stdout).values())[0]
        print("[OK] Registered tasks:")
        for task in tasks:
            print(f"  - {task}")
    
    print()
    return code == 0


def test_dashboard():
    """Test Dashboard access"""
    print("=" * 60)
    print("Test 4: Streamlit Dashboard")
    print("=" * 60)
    
    # Check Dashboard container status
    cmd = "docker ps --filter name=cae_dashboard --format '{{.Status}}'"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and "Up" in stdout:
        print("[OK] Dashboard is running")
        print("  URL: http://localhost:8501")
        
        # Test HTTP connection
        cmd = "curl -s -o /dev/null -w '%{http_code}' http://localhost:8501"
        stdout, stderr, code = run_command(cmd)
        if stdout == "200":
            print("[OK] Dashboard accessible (HTTP 200)")
        else:
            print(f"[FAIL] Dashboard not accessible (HTTP {stdout})")
    else:
        print("[FAIL] Dashboard is not running")
    
    print()
    return code == 0


def test_flower():
    """Test Flower monitoring"""
    print("=" * 60)
    print("Test 5: Flower Monitoring")
    print("=" * 60)
    
    # Check Flower container status
    cmd = "docker ps --filter name=cae_flower --format '{{.Status}}'"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and "Up" in stdout:
        print("[OK] Flower is running")
        print("  URL: http://localhost:5555")
        
        # Test HTTP connection
        cmd = "curl -s -o /dev/null -w '%{http_code}' http://localhost:5555"
        stdout, stderr, code = run_command(cmd)
        if stdout == "200":
            print("[OK] Flower accessible (HTTP 200)")
        else:
            print(f"[FAIL] Flower not accessible (HTTP {stdout})")
    else:
        print("[FAIL] Flower is not running")
    
    print()
    return code == 0


def test_database():
    """Test database connection"""
    print("=" * 60)
    print("Test 6: Database Connection")
    print("=" * 60)
    
    # Test PostgreSQL connection
    cmd = "docker exec cae_postgres psql -U cae_user -d cae_platform -c 'SELECT version();'"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0:
        print("[OK] PostgreSQL connection successful")
        print(f"  Database version: {stdout.split()[2]}")
    else:
        print("[FAIL] PostgreSQL connection failed")
    
    # Test Redis connection
    cmd = "docker exec cae_redis redis-cli ping"
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and "PONG" in stdout:
        print("[OK] Redis connection successful")
    else:
        print("[FAIL] Redis connection failed")
    
    print()
    return code == 0


def main():
    """Main test function"""
    print("\n")
    print("CAE Digital Twin Platform - System Test")
    print("=" * 60)
    print()
    
    # Run all tests
    results = {
        "Dashboard": test_dashboard(),
        "Flower": test_flower(),
        "Gmsh Mesh Generation": test_gmsh(),
        "CalculiX Simulation": test_calculix(),
        "Celery Task Queue": test_celery(),
        "Database": test_database(),
    }
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{name:25s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! System is running normally.")
    else:
        print(f"\n{total - passed} tests failed, please check logs.")
    
    print()


if __name__ == "__main__":
    main()
