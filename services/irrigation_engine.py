def calculate_crop_water_requirement(et0, crop_coefficient):
    """
    Calculate Crop Evapotranspiration (ETc).
    ETc = ET0 × Kc
    """
    if et0 < 0:
        raise ValueError("ET0 cannot be negative.")

    if crop_coefficient <= 0:
        raise ValueError("Crop coefficient must be positive.")

    return et0 * crop_coefficient


def calculate_total_available_water(
    field_capacity,
    wilting_point,
    root_depth
):
    """
    Calculate Total Available Water (TAW) in mm.
    """
    if not 0 <= wilting_point < field_capacity <= 100:
        raise ValueError("Invalid soil moisture limits.")

    if root_depth <= 0:
        raise ValueError("Root depth must be positive.")

    taw = (
        1000
        * ((field_capacity - wilting_point) / 100)
        * root_depth
    )

    return taw


def calculate_readily_available_water(
    taw,
    depletion_fraction
):
    """
    Calculate Readily Available Water (RAW) in mm.
    RAW = TAW × Depletion Fraction
    """
    if taw < 0:
        raise ValueError("TAW cannot be negative.")

    if not 0 < depletion_fraction <= 1:
        raise ValueError("Depletion fraction must be between 0 and 1.")

    return taw * depletion_fraction


def calculate_irrigation_requirement(
    taw,
    current_depletion,
    net_irrigation_efficiency=0.90
):
    """
    Calculate net and gross irrigation requirement in mm.
    """
    if taw < 0:
        raise ValueError("TAW cannot be negative.")

    if current_depletion < 0:
        raise ValueError("Depletion cannot be negative.")

    if not 0 < net_irrigation_efficiency <= 1:
        raise ValueError("Efficiency must be greater than 0 and at most 1.")

    # Net irrigation cannot exceed total available water
    net_irrigation = min(current_depletion, taw)

    # Adjust for irrigation system efficiency
    gross_irrigation = (
        net_irrigation / net_irrigation_efficiency
    )

    return net_irrigation, gross_irrigation
