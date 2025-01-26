import pytest
from pathlib import Path
import yaml
from src.world.terrain_templates import TerrainTemplate, TerrainTemplateManager
from src.world.terrain_settings import TerrainSettings, ErosionSettings

@pytest.fixture
def erosion_settings():
    return ErosionSettings(
        droplets=1000,
        inertia=0.05,
        capacity=4.0,
        deposition=0.1,
        erosion=0.3,
        evaporation=0.02,
        min_slope=0.01
    )

@pytest.fixture
def terrain_settings(erosion_settings):
    return TerrainSettings(
        width=128,
        height=128,
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
        scale=50.0,
        height_power=1.2,
        water_level=0.4,
        land_scale=0.3,
        seed=42,
        erosion=erosion_settings
    )

@pytest.fixture
def template_manager(tmp_path):
    """Create a template manager with a temporary directory."""
    return TerrainTemplateManager(templates_dir=tmp_path)

def test_terrain_template_creation(terrain_settings):
    """Test creating a TerrainTemplate instance."""
    template = TerrainTemplate(
        name="Test Template",
        description="A test template",
        settings=terrain_settings
    )
    
    assert template.name == "Test Template"
    assert template.description == "A test template"
    assert template.settings == terrain_settings

def test_template_manager_initialization(template_manager):
    """Test that TerrainTemplateManager initializes correctly."""
    assert template_manager.templates == {}
    assert template_manager.templates_dir.exists()

def test_save_template(template_manager, terrain_settings):
    """Test saving a template to disk."""
    success = template_manager.save_template(
        "Test Template",
        "A test template",
        terrain_settings
    )
    
    assert success
    template_path = template_manager.templates_dir / "test_template.yaml"
    assert template_path.exists()
    
    # Verify saved content
    with open(template_path, 'r') as f:
        saved_data = yaml.safe_load(f)
    
    assert saved_data['name'] == "Test Template"
    assert saved_data['description'] == "A test template"
    assert saved_data['settings']['width'] == 128

def test_load_templates(template_manager, terrain_settings):
    """Test loading templates from disk."""
    # Save a template first
    template_manager.save_template(
        "Test Template",
        "A test template",
        terrain_settings
    )
    
    # Create new manager instance to test loading
    new_manager = TerrainTemplateManager(templates_dir=template_manager.templates_dir)
    
    assert "Test Template" in new_manager.templates
    loaded_template = new_manager.templates["Test Template"]
    assert loaded_template.settings.width == terrain_settings.width
    assert loaded_template.settings.height == terrain_settings.height

def test_get_template(template_manager, terrain_settings):
    """Test retrieving a template by name."""
    template_manager.save_template(
        "Test Template",
        "A test template",
        terrain_settings
    )
    
    template = template_manager.get_template("Test Template")
    assert template is not None
    assert template.name == "Test Template"
    
    # Test nonexistent template
    assert template_manager.get_template("Nonexistent") is None

def test_list_templates(template_manager, terrain_settings):
    """Test listing all available templates."""
    # Save multiple templates
    templates_data = [
        ("Template1", "Description 1", terrain_settings),
        ("Template2", "Description 2", terrain_settings),
    ]
    
    for name, desc, settings in templates_data:
        template_manager.save_template(name, desc, settings)
    
    template_list = template_manager.list_templates()
    assert len(template_list) == 2
    assert template_list["Template1"] == "Description 1"
    assert template_list["Template2"] == "Description 2"

def test_invalid_template_loading(template_manager, tmp_path):
    """Test handling of invalid template files."""
    # Create an invalid template file
    invalid_file = tmp_path / "invalid.yaml"
    with open(invalid_file, 'w') as f:
        f.write("invalid: yaml: content")
    
    # Create new manager to test loading
    new_manager = TerrainTemplateManager(templates_dir=tmp_path)
    assert len(new_manager.templates) == 0

def test_template_file_naming(template_manager, terrain_settings):
    """Test template file naming convention."""
    template_manager.save_template(
        "Complex Name With Spaces",
        "Test description",
        terrain_settings
    )
    
    expected_path = template_manager.templates_dir / "complex_name_with_spaces.yaml"
    assert expected_path.exists()

def test_template_overwrite(template_manager, terrain_settings):
    """Test overwriting an existing template."""
    # Save initial template
    template_manager.save_template(
        "Test Template",
        "Initial description",
        terrain_settings
    )
    
    # Save template with same name but different description
    success = template_manager.save_template(
        "Test Template",
        "Updated description",
        terrain_settings
    )
    
    assert success
    template = template_manager.get_template("Test Template")
    assert template.description == "Updated description"
