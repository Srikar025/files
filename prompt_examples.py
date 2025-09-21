"""
Prompt examples and suggestions for AI Kolam generation
"""

# Categorized prompt examples
PROMPT_CATEGORIES = {
    "🌸 Floral Patterns": [
        "Create a beautiful 8-petaled lotus Kolam with rotational symmetry",
        "Generate a rose flower Kolam with intricate petal details",
        "Design a simple 6-petaled flower Kolam with a center dot",
        "Make a complex floral mandala with multiple flower layers",
        "Create a sunflower-inspired Kolam with radiating petals",
        "Design a cherry blossom Kolam with delicate petal shapes"
    ],
    
    "🔄 Geometric Patterns": [
        "Generate a perfect diamond Kolam with bilateral symmetry",
        "Create a complex square mandala with nested geometric shapes",
        "Design a hexagonal Kolam with 6-fold rotational symmetry",
        "Make a triangular Kolam with intricate internal patterns",
        "Create a circular Kolam with concentric geometric rings",
        "Design a star-shaped Kolam with radiating geometric lines"
    ],
    
    "🌟 Traditional Designs": [
        "Create a traditional South Indian Kolam with cultural significance",
        "Generate a classical Tamil Kolam with traditional motifs",
        "Design a festival Kolam with auspicious symbols",
        "Make a wedding Kolam with traditional decorative elements",
        "Create a Diwali Kolam with traditional lamp motifs",
        "Design a temple Kolam with religious symbolism"
    ],
    
    "🎨 Artistic Patterns": [
        "Generate a modern abstract Kolam with flowing curves",
        "Create a mandala-inspired Kolam with intricate details",
        "Design a spiral Kolam with mathematical precision",
        "Make a web-like Kolam with interconnected lines",
        "Create a wave-pattern Kolam with fluid movements",
        "Design a maze-like Kolam with complex pathways"
    ],
    
    "⭐ Simple Patterns": [
        "Create a simple 3x3 dot Kolam for beginners",
        "Generate a basic symmetric Kolam with 4 dots",
        "Design a minimal Kolam with clean lines",
        "Make a simple flower Kolam with 5 petals",
        "Create an easy geometric Kolam with squares",
        "Design a beginner-friendly spiral Kolam"
    ],
    
    "🔥 Complex Patterns": [
        "Generate an extremely intricate Kolam with 50+ dots",
        "Create a multi-layered Kolam with overlapping patterns",
        "Design a fractal-inspired Kolam with recursive elements",
        "Make a complex mandala with multiple symmetry axes",
        "Create an elaborate temple Kolam with detailed motifs",
        "Design a master-level Kolam with mathematical precision"
    ]
}

# Complexity-based suggestions
COMPLEXITY_PROMPTS = {
    "Beginner (1-3)": [
        "Simple 3-dot triangle Kolam",
        "Basic 4-dot square pattern",
        "Easy 5-petal flower Kolam",
        "Simple cross-shaped Kolam",
        "Basic diamond with center dot"
    ],
    
    "Intermediate (4-6)": [
        "8-petal flower with rotational symmetry",
        "Complex diamond with internal patterns",
        "Spiral Kolam with 3 turns",
        "Geometric mandala with nested shapes",
        "Traditional 9-dot Kolam with connections"
    ],
    
    "Advanced (7-10)": [
        "Intricate temple Kolam with 20+ dots",
        "Complex mandala with multiple symmetry axes",
        "Fractal-inspired Kolam with recursive patterns",
        "Elaborate festival Kolam with cultural motifs",
        "Master-level Kolam with mathematical precision"
    ]
}

# Symmetry-based suggestions
SYMMETRY_PROMPTS = {
    "Rotational Symmetry": [
        "Create a Kolam with 4-fold rotational symmetry",
        "Generate a pattern with 6-fold rotational symmetry",
        "Design an 8-fold symmetric Kolam",
        "Make a pattern with perfect rotational balance"
    ],
    
    "Bilateral Symmetry": [
        "Create a Kolam with perfect bilateral symmetry",
        "Generate a pattern symmetric across vertical axis",
        "Design a Kolam with horizontal symmetry",
        "Make a pattern with diagonal symmetry"
    ],
    
    "Multiple Symmetries": [
        "Create a Kolam with both rotational and bilateral symmetry",
        "Generate a pattern with multiple symmetry axes",
        "Design a Kolam with complex symmetry combinations"
    ]
}

# Cultural context prompts
CULTURAL_PROMPTS = {
    "Festivals": [
        "Create a Diwali Kolam with lamp motifs",
        "Generate a Pongal Kolam with harvest symbols",
        "Design a Navaratri Kolam with goddess motifs",
        "Make a wedding Kolam with auspicious symbols"
    ],
    
    "Religious": [
        "Create a temple Kolam with divine symbols",
        "Generate a prayer Kolam with sacred geometry",
        "Design a blessing Kolam with positive energy",
        "Make a meditation Kolam with calming patterns"
    ],
    
    "Seasonal": [
        "Create a spring Kolam with flower motifs",
        "Generate a monsoon Kolam with water patterns",
        "Design a harvest Kolam with abundance symbols",
        "Make a winter Kolam with warm patterns"
    ]
}

def get_random_prompt(category=None):
    """Get a random prompt from a specific category or all categories"""
    if category and category in PROMPT_CATEGORIES:
        import random
        return random.choice(PROMPT_CATEGORIES[category])
    else:
        import random
        all_prompts = []
        for prompts in PROMPT_CATEGORIES.values():
            all_prompts.extend(prompts)
        return random.choice(all_prompts)

def get_prompts_by_complexity(complexity_level):
    """Get prompts based on complexity level"""
    if complexity_level in COMPLEXITY_PROMPTS:
        return COMPLEXITY_PROMPTS[complexity_level]
    return []

def get_prompts_by_symmetry(symmetry_type):
    """Get prompts based on symmetry type"""
    if symmetry_type in SYMMETRY_PROMPTS:
        return SYMMETRY_PROMPTS[symmetry_type]
    return []

def get_prompts_by_culture(cultural_type):
    """Get prompts based on cultural context"""
    if cultural_type in CULTURAL_PROMPTS:
        return CULTURAL_PROMPTS[cultural_type]
    return []
