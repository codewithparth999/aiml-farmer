from services.irrigation_engine import (
    calculate_crop_water_requirement,
    calculate_total_available_water,
    calculate_readily_available_water,
    calculate_irrigation_requirement
)


def generate_irrigation_advisory(
    field_capacity,
    wilting_point,
    current_moisture,
    root_depth,
    et0,
    crop_coefficient,
    depletion_fraction,
    field_area,
    forecast_rain=0,
    irrigation_efficiency=0.90
):
    # 1. Input validation
    if field_area <= 0:
        raise ValueError("Field area must be positive.")

    if not 0 <= wilting_point < field_capacity <= 100:
        raise ValueError("Field Capacity must be greater than Wilting Point.")

    if not wilting_point <= current_moisture <= field_capacity:
        raise ValueError("Current moisture must be between Wilting Point and Field Capacity.")

    if root_depth <= 0:
        raise ValueError("Root depth must be positive.")

    if et0 < 0 or forecast_rain < 0:
        raise ValueError("ET0 and rainfall cannot be negative.")

    if crop_coefficient <= 0:
        raise ValueError("Crop coefficient must be positive.")

    if not 0 < depletion_fraction <= 1:
        raise ValueError("Depletion fraction must be between 0 and 1.")

    if not 0 < irrigation_efficiency <= 1:
        raise ValueError("Irrigation efficiency must be between 0 and 1.")

    # 2. Crop water requirement
    etc = calculate_crop_water_requirement(
        et0,
        crop_coefficient
    )

    # 3. Soil water calculations
    taw = calculate_total_available_water(
        field_capacity,
        wilting_point,
        root_depth
    )

    raw = calculate_readily_available_water(
        taw,
        depletion_fraction
    )

    # 4. Current soil water depletion
    depletion = (
        (field_capacity - current_moisture)
        / 100
    ) * 1000 * root_depth

    # 5. Rainfall adjustment
    # Assumption: all forecast rainfall is effective.
    # Real effective rainfall may be lower.
    adjusted_depletion = max(
        0,
        depletion - forecast_rain
    )

    # 6. Irrigation decision
    if adjusted_depletion >= raw:
        decision = "IRRIGATE NOW"
        reason = (
            "Soil water depletion has reached or crossed "
            "the readily available water threshold."
        )

    elif adjusted_depletion >= raw * 0.75:
        decision = "MONITOR"
        reason = (
            "Soil water depletion is approaching "
            "the irrigation threshold."
        )

    else:
        decision = "WAIT"
        reason = (
            "Soil water depletion is currently below "
            "the irrigation threshold."
        )

    # 7. Irrigation quantity
    if decision == "IRRIGATE NOW":
        net, gross = calculate_irrigation_requirement(
            taw,
            adjusted_depletion,
            irrigation_efficiency
        )
    else:
        net, gross = 0, 0

    # 8. Water volume
    water_liters = gross * field_area * 10000

    return {
        "decision": decision,
        "reason": reason,
        "etc_mm_day": round(etc, 2),
        "total_available_water_mm": round(taw, 2),
        "readily_available_water_mm": round(raw, 2),
        "current_depletion_mm": round(depletion, 2),
        "adjusted_depletion_mm": round(adjusted_depletion, 2),
        "net_irrigation_mm": round(net, 2),
        "gross_irrigation_mm": round(gross, 2),
        "water_required_liters": round(water_liters, 2)
    }