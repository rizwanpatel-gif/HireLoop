"""
AI Service Configuration for Interview Scheduling System
Handles OpenRouter API setup and model configurations
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AIModel(Enum):
    """Available AI models with cost and performance characteristics"""
    CLAUDE_HAIKU = "anthropic/claude-3-haiku"      # Most cost-effective
    CLAUDE_SONNET = "anthropic/claude-3-sonnet"    # Balanced performance/cost
    GPT_3_5_TURBO = "openai/gpt-3.5-turbo"        # Fast and reliable
    GPT_4_TURBO = "openai/gpt-4-turbo"            # High quality, more expensive
    LLAMA_3_70B = "meta-llama/llama-3-70b-instruct"  # Open source option

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    max_tokens: int
    temperature: float
    cost_per_1k_tokens: float
    recommended_use: str
    features: List[str]

class AIConfig:
    """
    Configuration management for AI Service
    """
    
    # Model configurations optimized for interview scheduling tasks
    MODEL_CONFIGS = {
        AIModel.CLAUDE_HAIKU.value: ModelConfig(
            name="Claude-3-Haiku",
            max_tokens=4000,
            temperature=0.3,
            cost_per_1k_tokens=0.00025,
            recommended_use="Cost-effective candidate analysis and interviewer matching",
            features=["fast_response", "structured_output", "cost_effective", "reliable"]
        ),
        AIModel.CLAUDE_SONNET.value: ModelConfig(
            name="Claude-3-Sonnet", 
            max_tokens=4000,
            temperature=0.3,
            cost_per_1k_tokens=0.003,
            recommended_use="Detailed analysis and complex reasoning tasks",
            features=["high_quality", "complex_reasoning", "detailed_analysis", "balanced_cost"]
        ),
        AIModel.GPT_3_5_TURBO.value: ModelConfig(
            name="GPT-3.5-Turbo",
            max_tokens=4000, 
            temperature=0.3,
            cost_per_1k_tokens=0.0015,
            recommended_use="General purpose interview tasks with good performance",
            features=["fast", "reliable", "general_purpose", "good_json"]
        ),
        AIModel.GPT_4_TURBO.value: ModelConfig(
            name="GPT-4-Turbo",
            max_tokens=4000,
            temperature=0.3,
            cost_per_1k_tokens=0.01,
            recommended_use="Premium analysis for senior positions and complex evaluations",
            features=["highest_quality", "complex_reasoning", "premium", "detailed"]
        ),
        AIModel.LLAMA_3_70B.value: ModelConfig(
            name="Llama-3-70B-Instruct",
            max_tokens=4000,
            temperature=0.3,
            cost_per_1k_tokens=0.0009,
            recommended_use="Open source alternative with good performance",
            features=["open_source", "good_performance", "cost_effective", "privacy_friendly"]
        )
    }
    
    # Default system prompts for different tasks
    SYSTEM_PROMPTS = {
        "candidate_analysis": """You are an expert technical recruiter and interview strategist. Analyze candidate profiles to provide comprehensive assessments for interview planning.

Your analysis should be thorough, objective, and actionable. Focus on:
1. Technical competency assessment based on skills and experience
2. Experience level evaluation relative to position requirements
3. Skill-position alignment and gaps identification
4. Cultural fit indicators from background and communication
5. Interview strategy recommendations and focus areas

Provide scores on a 0-100 scale with specific justification. Be constructive but honest about weaknesses and areas for improvement.

CRITICAL: Respond ONLY with valid JSON in the exact format specified. No additional text or explanations outside the JSON structure.""",

        "interviewer_matching": """You are an expert interview coordinator specializing in optimal candidate-interviewer pairing. Your role is to match candidates with interviewers who will provide the most effective assessment.

Consider these key factors:
1. Technical expertise alignment - interviewer should have relevant skills to assess candidate
2. Experience level compatibility - appropriate seniority gap for meaningful evaluation  
3. Interview type specialization - interviewer's strength in the specific interview format
4. Past performance metrics - track record of successful assessments
5. Skill complementarity - interviewer can identify both strengths and gaps

For technical interviews, prioritize deep technical skill overlap. For behavioral interviews, focus on cultural assessment expertise.

Provide objective scoring with specific technical reasoning for each match.

CRITICAL: Respond ONLY with valid JSON array. No additional text or markdown formatting.""",

        "question_generation": """You are an expert interview designer creating targeted, high-quality interview questions. Design questions that:

1. Assess candidate skills directly relevant to the position requirements
2. Match the interviewer's expertise areas for credible evaluation
3. Are appropriate for the interview type and candidate's experience level
4. Include meaningful follow-up questions that reveal depth of knowledge
5. Cover both technical depth and practical application/problem-solving
6. Provide clear evaluation criteria for consistent assessment

Questions should be:
- Specific and actionable (not generic)
- Progressive in difficulty when appropriate
- Role-relevant with real-world applicability
- Clear in their assessment intent
- Time-appropriate for interview duration

CRITICAL: Respond ONLY with valid JSON in the exact format specified."""
    }
    
    # Interview type configurations
    INTERVIEW_TYPE_CONFIGS = {
        "technical": {
            "typical_duration": 60,
            "question_categories": ["coding", "system_design", "algorithms", "architecture"],
            "assessment_focus": ["problem_solving", "code_quality", "technical_depth", "communication"],
            "recommended_question_count": 8
        },
        "behavioral": {
            "typical_duration": 45,
            "question_categories": ["leadership", "teamwork", "conflict_resolution", "adaptability"],
            "assessment_focus": ["cultural_fit", "communication", "past_experience", "problem_solving"],
            "recommended_question_count": 6
        },
        "system_design": {
            "typical_duration": 90,
            "question_categories": ["architecture", "scalability", "databases", "trade_offs"],
            "assessment_focus": ["system_thinking", "scalability_awareness", "trade_off_analysis", "real_world_experience"],
            "recommended_question_count": 3
        },
        "cultural_fit": {
            "typical_duration": 30,
            "question_categories": ["values", "work_style", "team_dynamics", "company_mission"],
            "assessment_focus": ["value_alignment", "team_fit", "communication_style", "motivation"],
            "recommended_question_count": 5
        },
        "coding": {
            "typical_duration": 75,
            "question_categories": ["algorithms", "data_structures", "debugging", "optimization"],
            "assessment_focus": ["coding_skills", "problem_solving", "code_quality", "testing_mindset"],
            "recommended_question_count": 4
        }
    }
    
    @classmethod
    def get_model_config(cls, model: str) -> ModelConfig:
        """Get configuration for a specific model"""
        return cls.MODEL_CONFIGS.get(model, cls.MODEL_CONFIGS[AIModel.CLAUDE_HAIKU.value])
    
    @classmethod
    def get_recommended_model(cls, use_case: str = "general") -> str:
        """
        Get recommended model for specific use case
        
        Args:
            use_case: 'cost_effective', 'high_quality', 'balanced', 'general'
            
        Returns:
            Model identifier string
        """
        recommendations = {
            "cost_effective": AIModel.CLAUDE_HAIKU.value,
            "high_quality": AIModel.CLAUDE_SONNET.value,
            "balanced": AIModel.GPT_3_5_TURBO.value,
            "premium": AIModel.GPT_4_TURBO.value,
            "general": AIModel.CLAUDE_HAIKU.value
        }
        
        return recommendations.get(use_case, AIModel.CLAUDE_HAIKU.value)
    
    @classmethod
    def get_system_prompt(cls, task_type: str) -> str:
        """Get system prompt for specific task type"""
        return cls.SYSTEM_PROMPTS.get(task_type, cls.SYSTEM_PROMPTS["candidate_analysis"])
    
    @classmethod
    def get_interview_config(cls, interview_type: str) -> Dict:
        """Get configuration for specific interview type"""
        return cls.INTERVIEW_TYPE_CONFIGS.get(interview_type, cls.INTERVIEW_TYPE_CONFIGS["technical"])
    
    @classmethod
    def validate_api_key(cls, api_key: str) -> bool:
        """
        Validate OpenRouter API key format
        
        Args:
            api_key: API key to validate
            
        Returns:
            bool: True if format appears valid
        """
        if not api_key:
            return False
        
        # OpenRouter API keys typically start with 'sk-or-' 
        if api_key.startswith('sk-or-') and len(api_key) > 20:
            return True
        
        # Also accept other formats for flexibility
        if len(api_key) > 20 and api_key.isalnum():
            return True
            
        return False
    
    @classmethod
    def get_cost_estimate(cls, model: str, token_count: int) -> float:
        """
        Estimate cost for API call
        
        Args:
            model: Model identifier
            token_count: Estimated token count
            
        Returns:
            Estimated cost in USD
        """
        config = cls.get_model_config(model)
        return (token_count / 1000) * config.cost_per_1k_tokens
    
    @classmethod
    def get_all_models_info(cls) -> Dict[str, Dict]:
        """Get information about all available models"""
        models_info = {}
        
        for model_id, config in cls.MODEL_CONFIGS.items():
            models_info[model_id] = {
                "name": config.name,
                "cost_per_1k_tokens": config.cost_per_1k_tokens,
                "max_tokens": config.max_tokens,
                "recommended_use": config.recommended_use,
                "features": config.features,
                "relative_cost": "low" if config.cost_per_1k_tokens < 0.001 else "medium" if config.cost_per_1k_tokens < 0.005 else "high"
            }
        
        return models_info

# Environment variable names
ENV_VARS = {
    "API_KEY": "OPENROUTER_API_KEY",
    "MODEL": "AI_MODEL",
    "TEMPERATURE": "AI_TEMPERATURE", 
    "MAX_TOKENS": "AI_MAX_TOKENS",
    "COST_LIMIT": "AI_DAILY_COST_LIMIT"
}

# Default configuration
DEFAULT_CONFIG = {
    "model": AIModel.CLAUDE_HAIKU.value,
    "temperature": 0.3,
    "max_tokens": 4000,
    "daily_cost_limit": 10.0,  # $10 daily limit
    "timeout": 30,
    "max_retries": 3
}

def load_ai_config() -> Dict:
    """
    Load AI configuration from environment variables with defaults
    
    Returns:
        Dictionary with AI configuration
    """
    config = DEFAULT_CONFIG.copy()
    
    # Load from environment variables
    if os.getenv(ENV_VARS["MODEL"]):
        config["model"] = os.getenv(ENV_VARS["MODEL"])
    
    if os.getenv(ENV_VARS["TEMPERATURE"]):
        try:
            config["temperature"] = float(os.getenv(ENV_VARS["TEMPERATURE"]))
        except ValueError:
            pass
    
    if os.getenv(ENV_VARS["MAX_TOKENS"]):
        try:
            config["max_tokens"] = int(os.getenv(ENV_VARS["MAX_TOKENS"]))
        except ValueError:
            pass
    
    if os.getenv(ENV_VARS["COST_LIMIT"]):
        try:
            config["daily_cost_limit"] = float(os.getenv(ENV_VARS["COST_LIMIT"]))
        except ValueError:
            pass
    
    return config

def create_ai_env_template() -> str:
    """
    Create a template .env file for AI configuration
    
    Returns:
        Template content as string
    """
    template = f"""# AI Service Configuration for Interview Scheduling System
# Get your OpenRouter API key from: https://openrouter.ai/keys

# Required: OpenRouter API Key
{ENV_VARS["API_KEY"]}=your_openrouter_api_key_here

# Optional: AI Model Selection (default: claude-3-haiku for cost-effectiveness)
# Options: {', '.join([model.value for model in AIModel])}
{ENV_VARS["MODEL"]}={DEFAULT_CONFIG["model"]}

# Optional: Model Parameters
{ENV_VARS["TEMPERATURE"]}={DEFAULT_CONFIG["temperature"]}
{ENV_VARS["MAX_TOKENS"]}={DEFAULT_CONFIG["max_tokens"]}

# Optional: Cost Control (daily limit in USD)
{ENV_VARS["COST_LIMIT"]}={DEFAULT_CONFIG["daily_cost_limit"]}

# Model Comparison:
# - claude-3-haiku: ${AIConfig.MODEL_CONFIGS[AIModel.CLAUDE_HAIKU.value].cost_per_1k_tokens}/1K tokens - Most cost-effective
# - claude-3-sonnet: ${AIConfig.MODEL_CONFIGS[AIModel.CLAUDE_SONNET.value].cost_per_1k_tokens}/1K tokens - Balanced quality/cost  
# - gpt-3.5-turbo: ${AIConfig.MODEL_CONFIGS[AIModel.GPT_3_5_TURBO.value].cost_per_1k_tokens}/1K tokens - Fast and reliable
# - gpt-4-turbo: ${AIConfig.MODEL_CONFIGS[AIModel.GPT_4_TURBO.value].cost_per_1k_tokens}/1K tokens - Highest quality

# For high-volume usage, Claude-3-Haiku provides the best cost/performance ratio
# For complex analysis of senior positions, consider Claude-3-Sonnet or GPT-4-Turbo
"""
    return template

if __name__ == "__main__":
    """
    Configuration utility and information display
    """
    print("🤖 AI Service Configuration")
    print("=" * 50)
    
    # Display available models
    print("\n📊 Available AI Models:")
    models_info = AIConfig.get_all_models_info()
    
    for model_id, info in models_info.items():
        print(f"\n{info['name']} ({model_id}):")
        print(f"  💰 Cost: ${info['cost_per_1k_tokens']}/1K tokens ({info['relative_cost']} cost)")
        print(f"  🎯 Use Case: {info['recommended_use']}")
        print(f"  ✨ Features: {', '.join(info['features'])}")
    
    # Display current configuration
    print(f"\n⚙️ Current Configuration:")
    config = load_ai_config()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Display cost estimates
    print(f"\n💰 Cost Estimates (per 1000 tokens):")
    sample_tokens = 1000
    for model_id in [AIModel.CLAUDE_HAIKU.value, AIModel.CLAUDE_SONNET.value, AIModel.GPT_3_5_TURBO.value]:
        cost = AIConfig.get_cost_estimate(model_id, sample_tokens)
        print(f"  {AIConfig.MODEL_CONFIGS[model_id].name}: ${cost:.6f}")
    
    # Check API key
    api_key = os.getenv(ENV_VARS["API_KEY"])
    if api_key:
        if AIConfig.validate_api_key(api_key):
            print(f"\n✅ OpenRouter API key found and validated")
        else:
            print(f"\n⚠️ OpenRouter API key found but format appears invalid")
    else:
        print(f"\n❌ OpenRouter API key not found")
        print(f"   Set {ENV_VARS['API_KEY']} environment variable")
        print(f"   Get your key from: https://openrouter.ai/keys")
    
    # Generate .env template
    print(f"\n📝 .env Template:")
    print("-" * 30)
    print(create_ai_env_template())
