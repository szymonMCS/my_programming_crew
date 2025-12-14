from pathlib import Path
from typing import Any
from pydantic import BaseModel
from crewai import Crew, Process

from my_programming_crew.crew import (
    EngineeringTeam,
    ModuleBreakdown,
    get_model_summary,
)

OUTPUT_DIR = Path("output")
JSON_DIR = OUTPUT_DIR / "json"

def sanitize_filename(name: str) -> str:
    """Oczyszcza nazwę pliku z niebezpiecznych znaków."""
    safe = "".join(c for c in name if c.isalnum() or c in ('_', '-', '.'))
    return f"output_{safe}" if not safe or safe.startswith('.') else safe

def save_result(output: BaseModel, filename: str) -> None:
    """
    Generyczna funkcja zapisu - obsługuje JSON + ekstrakcję pól code/content.
    
    Automatycznie wykrywa i zapisuje:
    - JSON dla każdego modelu Pydantic
    - Pole 'code' → {module_name}.py
    - Pole 'test_code' → test_implementation.py
    - Pole 'readme_content' → README.md
    - Pole 'main_app_code' → main_app.py + komponenty
    """
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    
    json_file = JSON_DIR / f"{filename}.json"
    json_file.write_text(output.model_dump_json(indent=2), encoding='utf-8')
    print(f"  [JSON] {json_file}")
    
    extractions = [
        (
            hasattr(output, 'code') and hasattr(output, 'module_name'),
            lambda o: OUTPUT_DIR / f"{sanitize_filename(o.module_name)}.py",
            lambda o: o.code
        ),
        (
            hasattr(output, 'test_code'),
            lambda _: OUTPUT_DIR / "test_implementation.py",
            lambda o: o.test_code
        ),
        (
            hasattr(output, 'readme_content'),
            lambda _: OUTPUT_DIR / "README.md",
            lambda o: o.readme_content
        ),
        (
            hasattr(output, 'main_app_code'),
            lambda _: OUTPUT_DIR / "main_app.py",
            lambda o: o.main_app_code
        ),
    ]
    
    for condition, path_fn, content_fn in extractions:
        if condition:
            file_path = path_fn(output)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content_fn(output), encoding='utf-8')
            print(f"  [FILE] {file_path}")
    
    if hasattr(output, 'component_files') and output.component_files:
        components_dir = OUTPUT_DIR / "components"
        components_dir.mkdir(parents=True, exist_ok=True)
        for name, code in output.component_files.items():
            comp_path = components_dir / sanitize_filename(name)
            comp_path.write_text(code, encoding='utf-8')
            print(f"  [COMPONENT] {comp_path}")

def print_model_stats(model: BaseModel) -> None:
    """Wyświetla podsumowanie modelu."""
    summary = get_model_summary(model)
    for key, value in summary.items():
        print(f"    {key}: {value}")

def run_phase_1(team: EngineeringTeam, requirements: str) -> ModuleBreakdown | None:
    """Faza 1: Analiza biznesowa i projektowanie architektury."""
    print("\n" + "=" * 70)
    print("PHASE 1: Analysis & Design")
    print("=" * 70)
    
    result = team.crew().kickoff(inputs={'requirements': requirements})
    
    module_breakdown = None
    for i, task_output in enumerate(result.tasks_output, 1):
        if task_output.pydantic:
            model = task_output.pydantic
            model_name = type(model).__name__
            print(f"\n  Task {i}: {model_name}")
            print_model_stats(model)
            save_result(model, f"01_{i:02d}_{model_name.lower()}")
            
            if isinstance(model, ModuleBreakdown):
                module_breakdown = model
    
    return module_breakdown

def run_phase_2(team: EngineeringTeam, module_breakdown: ModuleBreakdown) -> list:
    """Faza 2: Dynamiczna implementacja modułów."""
    print("\n" + "=" * 70)
    print("PHASE 2: Dynamic Implementation")
    print("=" * 70)
    print(f"\n  Modules to implement: {module_breakdown.total_modules}")
    print(f"  Integration order: {' → '.join(module_breakdown.integration_order)}")
    
    implementation_tasks = team.create_implementation_tasks(module_breakdown)
    
    crew_phase2 = Crew(
        agents=[team.backend_developer()],
        tasks=implementation_tasks,
        process=Process.sequential,
        verbose=True,
    )
    
    result = crew_phase2.kickoff()
    
    for i, task_output in enumerate(result.tasks_output, 1):
        if task_output.pydantic:
            model = task_output.pydantic
            print(f"\n  Module {i}: {model.module_name}")
            print_model_stats(model)
            save_result(model, f"02_{i:02d}_{sanitize_filename(model.module_name)}")
    
    return implementation_tasks

def run_phase_3(team: EngineeringTeam, implementation_tasks: list) -> None:
    """Faza 3: Frontend, testy, review i dokumentacja."""
    print("\n" + "=" * 70)
    print("PHASE 3: Frontend, Testing & QA")
    print("=" * 70)
    
    final_tasks = [
        team.frontend_task(),
        team.test_planning_task(),
        team.test_execution_task(),
        team.code_review_task(),
        team.documentation_task(),
    ]
    
    for task in final_tasks:
        task.context = implementation_tasks
    
    crew_phase3 = Crew(
        agents=[
            team.frontend_engineer(),
            team.test_planner(),
            team.test_engineer(),
            team.code_reviewer(),
            team.documentation_writer(),
        ],
        tasks=final_tasks,
        process=Process.sequential,
        verbose=True,
    )
    
    result = crew_phase3.kickoff()
    
    task_names = ["frontend", "test_plan", "test_impl", "code_review", "docs"]
    for i, (task_output, name) in enumerate(zip(result.tasks_output, task_names), 1):
        if task_output.pydantic:
            model = task_output.pydantic
            model_name = type(model).__name__
            print(f"\n  Task {i}: {model_name}")
            print_model_stats(model)
            save_result(model, f"03_{i:02d}_{name}")

def run_engineering_pipeline(requirements: str) -> None:
    """Uruchamia pełny pipeline inżynieryjny."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    team = EngineeringTeam()
    
    module_breakdown = run_phase_1(team, requirements)
    if not module_breakdown:
        print("\n[ERROR] ModuleBreakdown not found in Phase 1!")
        return
    
    implementation_tasks = run_phase_2(team, module_breakdown)
    
    run_phase_3(team, implementation_tasks)
    
    print("\n" + "=" * 70)
    print("SUCCESS - ALL PHASES COMPLETED!")
    print("=" * 70)
    print(f"\nOutput saved to: {OUTPUT_DIR.absolute()}")
    print(f"  - JSON: {JSON_DIR}")
    print(f"  - Code: {OUTPUT_DIR}")

def main():
    """Punkt wejścia."""
    requirements = """
    A simple account management system for a trading simulation platform.
    The system should allow users to create an account, deposit funds, and withdraw funds.
    The system should allow users to record that they have bought or sold shares, providing a quantity.
    The system should calculate the total value of the user's portfolio, and the profit or loss from the initial deposit.
    The system should be able to report the holdings of the user at any point in time.
    The system should be able to report the profit or loss of the user at any point in time.
    The system should be able to list the transactions that the user has made over time.
    The system should prevent the user from withdrawing funds that would leave them with a negative balance, or
    from buying more shares than they can afford, or selling shares that they don't have.
    The system has access to a function get_share_price(symbol) which returns the current price of a share, 
    and includes a test implementation that returns fixed prices for AAPL, TSLA, GOOGL.
    """
    
    try:
        run_engineering_pipeline(requirements)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
