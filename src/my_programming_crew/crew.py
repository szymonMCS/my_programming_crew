from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class BusinessRequirements(BaseModel):
    """Model dla analizy biznesowej."""
    user_stories: List[str] = Field(default_factory=list, description="User stories: Jako... Chcę... Aby...")
    business_rules: List[str] = Field(default_factory=list, description="Reguły biznesowe i ograniczenia")
    data_models: List[Dict[str, Any]] = Field(default_factory=list, description="Modele danych (encje i atrybuty)")
    quality_requirements: Dict[str, str] = Field(default_factory=dict, description="Wymagania jakościowe")
    scope_clarity_score: int = Field(default=7, ge=1, le=10, description="Ocena jakości zakresu (1-10)")
    recommended_modules: List[str] = Field(default_factory=list, description="Zalecane moduły")
    complexity_assessment: Literal["simple", "medium", "complex"] = Field(description="Ocena złożoności")

class ClassSpec(BaseModel):
    """Specyfikacja pojedynczej klasy."""
    class_name: str = Field(description="Nazwa klasy (PascalCase)")
    module_path: str = Field(description="Ścieżka pliku, np. 'account_core/account.py'")
    responsibility: str = Field(description="Odpowiedzialność klasy")
    methods: List[str] = Field(default_factory=list, description="Metody do implementacji")
    attributes: List[str] = Field(default_factory=list, description="Atrybuty klasy")
    dependencies: List[str] = Field(default_factory=list, description="Zależności")
    complexity: Literal["simple", "medium", "complex"] = Field(default="medium")

class ModuleSpec(BaseModel):
    """Specyfikacja pojedynczego modułu."""
    module_name: str = Field(description="Nazwa modułu")
    description: str = Field(description="Opis odpowiedzialności modułu")
    classes: List[ClassSpec] = Field(default_factory=list, description="Klasy w module")
    dependencies: List[str] = Field(default_factory=list, description="Zależności od innych modułów")

class ModuleBreakdown(BaseModel):
    """Kluczowy model definiujący całą specyfikację aplikacji."""
    project_name: str = Field(description="Nazwa projektu")
    total_modules: int = Field(description="Liczba modułów")
    total_classes: int = Field(description="Liczba klas do implementacji")
    modules: List[ModuleSpec] = Field(default_factory=list, description="Lista modułów")
    integration_order: List[str] = Field(default_factory=list, description="Kolejność integracji")
    dependency_graph: str = Field(description="Graf zależności (ASCII/Mermaid)")
    architecture_notes: str = Field(description="Notatki architektoniczne")

class BackendArchitecture(BaseModel):
    """Model dla architektury backendu."""
    database_design: Optional[str] = Field(default=None, description="Projekt bazy danych")
    api_design: Optional[str] = Field(default=None, description="Projekt API")
    service_layer: Optional[str] = Field(default=None, description="Warstwa usług")
    data_access_layer: Optional[str] = Field(default=None, description="Warstwa dostępu do danych")
    architecture_diagram: str = Field(description="Diagram architektury")

class CodeModule(BaseModel):
    """Model dla implementacji modułu."""
    module_name: str = Field(description="Nazwa modułu")
    file_path: str = Field(description="Ścieżka pliku")
    code: str = Field(description="Kod modułu (bez Markdown)")
    classes_implemented: List[str] = Field(default_factory=list)
    methods_implemented: List[str] = Field(default_factory=list)
    has_type_hints: bool = Field(default=True)
    has_docstrings: bool = Field(default=True)
    has_error_handling: bool = Field(default=True)
    public_interface: List[str] = Field(default_factory=list)

class FrontendOutput(BaseModel):
    """Model dla frontendu."""
    main_app_code: str = Field(description="Kod głównego pliku")
    component_files: Dict[str, str] = Field(default_factory=dict, description="nazwa → kod komponentu")
    styles_code: Optional[str] = Field(default=None, description="Kod CSS")
    total_files: int = Field(description="Liczba plików")
    features_implemented: List[str] = Field(default_factory=list)
    usage_instructions: str = Field(description="Instrukcje uruchomienia")

class TestCase(BaseModel):
    """Specyfikacja przypadku testowego."""
    test_name: str = Field(description="Nazwa testu (test_should_...)")
    test_type: Literal["unit", "integration", "negative", "boundary"] = Field(description="Typ testu")
    target_function: str = Field(description="Testowana funkcja/metoda")
    scenario: str = Field(description="Scenariusz testowy")
    expected_outcome: str = Field(description="Oczekiwany wynik")

class TestSuite(BaseModel):
    """Test suite dla modułu/klasy."""
    suite_name: str = Field(description="Nazwa suite")
    target_module: str = Field(description="Moduł/klasa do testowania")
    test_cases: List[TestCase] = Field(default_factory=list)
    coverage_target: int = Field(default=80, ge=0, le=100)

class TestPlan(BaseModel):
    """Plan testów."""
    project_name: str
    test_strategy: str
    test_suites: List[TestSuite] = Field(default_factory=list)
    total_test_cases: int = Field(default=0)
    framework: str = Field(default="pytest")
    coverage_target_overall: int = Field(default=80, ge=0, le=100)

class TestImplementation(BaseModel):
    """Implementacja testów."""
    test_code: str = Field(description="Kod testów (bez Markdown)")
    test_cases_count: int
    coverage_areas: List[str] = Field(default_factory=list)
    framework_used: str = Field(default="pytest")
    estimated_coverage_percent: Optional[int] = Field(default=None)

class CodeReviewFinding(BaseModel):
    """Pojedyncze znalezisko z code review."""
    category: Literal["quality", "security", "performance"] = Field(description="Kategoria")
    severity: Literal["critical", "high", "medium", "low", "informational"] = Field(description="Ważność")
    title: str
    description: str
    location: Optional[str] = Field(default=None)
    suggestion: Optional[str] = Field(default=None)

class CodeReview(BaseModel):
    """Model dla code review."""
    overall_rating: int = Field(ge=1, le=10)
    summary: str
    findings: List[CodeReviewFinding] = Field(default_factory=list)
    positive_highlights: List[str] = Field(default_factory=list)
    recommendation: Literal["APPROVE", "REQUEST CHANGES", "REJECT"]

class Documentation(BaseModel):
    """Model dla dokumentacji."""
    readme_content: str = Field(description="Zawartość README.md")
    api_documentation: Optional[str] = Field(default=None)
    user_guide: Optional[str] = Field(default=None)
    installation_steps: List[str] = Field(default_factory=list)
    usage_examples: List[str] = Field(default_factory=list)

def get_model_summary(model: BaseModel) -> dict[str, Any]:
    """Zwraca kluczowe metryki dla modelu (do logowania/wyświetlania)."""
    name = type(model).__name__
    
    summaries = {
        "BusinessRequirements": lambda m: {
            "user_stories": len(m.user_stories),
            "complexity": m.complexity_assessment
        },
        "ModuleBreakdown": lambda m: {
            "project": m.project_name,
            "modules": m.total_modules,
            "classes": m.total_classes
        },
        "CodeModule": lambda m: {
            "module": m.module_name,
            "classes": len(m.classes_implemented),
            "methods": len(m.methods_implemented)
        },
        "BackendArchitecture": lambda m: {
            "has_db": bool(m.database_design),
            "has_api": bool(m.api_design)
        },
        "FrontendOutput": lambda m: {
            "files": m.total_files,
            "components": len(m.component_files)
        },
        "TestPlan": lambda m: {
            "suites": len(m.test_suites),
            "cases": m.total_test_cases,
            "coverage_target": f"{m.coverage_target_overall}%"
        },
        "TestImplementation": lambda m: {
            "cases": m.test_cases_count,
            "coverage": f"~{m.estimated_coverage_percent}%"
        },
        "CodeReview": lambda m: {
            "rating": f"{m.overall_rating}/10",
            "findings": len(m.findings),
            "recommendation": m.recommendation
        },
        "Documentation": lambda m: {
            "steps": len(m.installation_steps),
            "examples": len(m.usage_examples)
        }
    }
    return summaries.get(name, lambda _: {})(model)

def format_class_specs(classes: List[ClassSpec]) -> str:
    """Formatuje specyfikacje klas do użycia w promptach."""
    return "\n".join(
        f"  - {cls.class_name}: {cls.responsibility}\n"
        f"    Methods: {', '.join(cls.methods)}\n"
        f"    Complexity: {cls.complexity}"
        for cls in classes
    )

@CrewBase
class EngineeringTeam:
    """
    Hierarchiczny zespół programistyczny z dynamicznym tworzeniem zadań.
    Proces: Sequential z kontekstem między zadaniami.
    """
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def engineering_lead(self) -> Agent:
        return Agent(config=self.agents_config['engineering_lead'], verbose=True)
    
    @agent
    def business_analyst(self) -> Agent:
        return Agent(config=self.agents_config['business_analyst'], verbose=True)
    
    @agent
    def backend_architect(self) -> Agent:
        return Agent(config=self.agents_config['backend_architect'], verbose=True)
    
    @agent
    def backend_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_developer'],
            verbose=True,
            allow_code_execution=False,
            code_execution_mode="safe",
        )
    
    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(config=self.agents_config['frontend_engineer'], verbose=True)
    
    @agent
    def test_planner(self) -> Agent:
        return Agent(config=self.agents_config['test_planner'], verbose=True)
    
    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
        )
    
    @agent
    def code_reviewer(self) -> Agent:
        return Agent(config=self.agents_config['code_reviewer'], verbose=True)
    
    @agent
    def documentation_writer(self) -> Agent:
        return Agent(config=self.agents_config['documentation_writer'], verbose=True)
    
    @task
    def business_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['business_analysis_task'],
            output_pydantic=BusinessRequirements,
        )
    
    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'],
            output_pydantic=ModuleBreakdown,
        )
    
    @task
    def architecture_task(self) -> Task:
        return Task(
            config=self.tasks_config['architecture_task'],
            output_pydantic=BackendArchitecture,
        )
    
    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'],
            output_pydantic=FrontendOutput,
        )
    
    @task
    def test_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_planning_task'],
            output_pydantic=TestPlan,
        )
    
    @task
    def test_execution_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_execution_task'],
            output_pydantic=TestImplementation,
        )
    
    @task
    def code_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_review_task'],
            output_pydantic=CodeReview,
        )
    
    @task
    def documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config['documentation_task'],
            output_pydantic=Documentation,
        )
    
    def create_implementation_tasks(self, module_breakdown: ModuleBreakdown) -> List[Task]:
        """
        Tworzy zadanie implementacyjne dla każdego modułu.
        Liczba zadań = liczba modułów (dynamiczna).
        """
        return [
            Task(
                description=f"""
                Implement the {module.module_name} module.

                Module: {module.module_name}
                Description: {module.description}

                Classes to implement:
                {format_class_specs(module.classes)}

                Dependencies: {', '.join(module.dependencies) or 'None'}

                Create production-quality Python code with type hints, docstrings, 
                error handling, and PEP 8 compliance.
                """,
                expected_output=f"""
                CodeModule for '{module.module_name}' with complete implementation.
                Output raw Python code in the 'code' field without markdown.
                """,
                agent=self.backend_developer(),
                output_pydantic=CodeModule,
                context=[
                    self.business_analysis_task(),
                    self.design_task(),
                    self.architecture_task()
                ]
            )
            for module in module_breakdown.modules
        ]
    
    @crew
    def crew(self) -> Crew:
        """Główny crew dla fazy 1 (analiza i design)."""
        return Crew(
            agents=self.agents,
            tasks=[
                self.business_analysis_task(),
                self.design_task(),
                self.architecture_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )
