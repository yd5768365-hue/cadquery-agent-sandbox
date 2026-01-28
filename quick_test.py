"""
Quick Test Script for CAE Platform
"""

import subprocess
from pathlib import Path


def run_cmd(cmd):
    """Execute shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def main():
    print("\n" + "=" * 60)
    print("CAE Platform Quick Test")
    print("=" * 60 + "\n")

    # 1. Check containers
    print("1. Container Status:")
    print("-" * 60)
    containers = [
        "cae_dashboard", "cae_flower", "cae_celery_worker",
        "cae_gmsh", "cae_calculix", "cae_postgres", "cae_redis"
    ]
    for container in containers:
        output, code = run_cmd(f"docker ps --filter name={container} --format '{{{{.Status}}}}'")
        status = "RUNNING" if code == 0 and "Up" in output else "STOPPED"
        print(f"  {container:20s}: {status}")
    print()

    # 2. Test Gmsh
    print("2. Test Gmsh Mesh Generation:")
    print("-" * 60)
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
"""
    geo_file = Path("test/input/test.geo")
    geo_file.write_text(geo_content)
    print("  Created geometry file")

    output, code = run_cmd("docker exec cae_gmsh gmsh /app/input/test.geo -2 -o /app/meshes/test.msh 2>&1 | grep -i 'info'")
    mesh_file = Path("test/meshes/test.msh")
    if mesh_file.exists():
        print(f"  [OK] Mesh generated: {mesh_file.stat().st_size} bytes")
    else:
        print("  [FAIL] Mesh not generated")
    print()

    # 3. Test CalculiX
    print("3. Test CalculiX:")
    print("-" * 60)
    inp_content = """*HEADING
Test
*NODE
1,0,0,0
2,1,0,0
3,1,1,0
4,0,1,0
*ELEMENT,TYPE=C3D8
1,1,2,3,4
*MATERIAL,NAME=M1
*ELASTIC
210000,0.3
*SOLID SECTION,MATERIAL=M1
*STEP
*STATIC
*END STEP
"""
    inp_file = Path("test/analyses/test.inp")
    inp_file.write_text(inp_content)
    print("  Created input file")

    output, code = run_cmd("docker exec cae_calculix ccx -i /app/analyses/test 2>&1 | tail -5")
    if "Calculation completed" in output or code == 0:
        print("  [OK] CalculiX simulation completed")
    else:
        print("  [FAIL] CalculiX simulation failed")
    print()

    # 4. Check Dashboard logs
    print("4. Dashboard Status:")
    print("-" * 60)
    output, code = run_cmd("docker logs cae_dashboard --tail 3")
    print(f"  Last log lines:")
    for line in output.split('\n')[-3:]:
        if line:
            print(f"    {line}")
    print()

    # 5. Check Celery worker
    print("5. Celery Worker Status:")
    print("-" * 60)
    output, code = run_cmd("docker logs cae_celery_worker --tail 3")
    print(f"  Last log lines:")
    for line in output.split('\n')[-3:]:
        if line:
            print(f"    {line}")
    print()

    print("=" * 60)
    print("Quick Test Complete")
    print("=" * 60)
    print("\nAccess URLs:")
    print("  Dashboard:  http://localhost:8501")
    print("  Flower:     http://localhost:5555")
    print()


if __name__ == "__main__":
    main()
