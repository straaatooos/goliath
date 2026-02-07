def items(type):
    items = []
    match type:
        case "Beam":
            items = [
                    "Status",
                    "Span",
                    "Slope",
                    "Roll",
                    "IsExternal",
                    "ThermalTransmittance",
                    "LoadBearing",
                    "FireRating"]
        case "Column":
            items = [
                    "Status",
                    "Slope",
                    "Roll",
                    "IsExternal",
                    "ThermalTransmittance",
                    "LoadBearing",
                    "FireRating"]
        case "Covering":
            items = [
                    "Status",
                    "AcousticRating",
                    "FlammabilityRating",
                    "FragilityRating",
                    "Combustible",
                    "SurfaceSpreadOfFlame",
                    "Finish",
                    "IsExternal",
                    "ThermalTransmittance",
                    "FireRating"]
        case "Door":
            items = [
                    "Status",
                    "FireRating",
                    "AcousticRating",
                    "SecurityRating",
                    "DurabilityRating",
                    "HygrothermalRating",
                    "WaterTightnessRating",
                    "MechnaicalLoadRating",
                    "WindLoadRating",
                    "IsExternal",
                    "ThermalTransmittance",
                    "GlazingAreaFraction",
                    "FireExit",
                    "HasDrive",
                    "SelfClosing",
                    "SmokeStop"]
        case "Member":
            items = [
                    "Status",
                    "Span",
                    "Slope",
                    "Roll",
                    "IsExternal",
                    "ThermalTransmittance",
                    "LoadBearing",
                    "FireRating"]            
        case "Railing":
            items = [
                    "Status",
                    "Height",
                    "Diameter",
                    "IsExternal"]
        case "Roof":
            items = [
                    "Status",
                    "Span",
                    "Slope",
                    "Roll",
                    "IsExternal",
                    "ThermalTransmittance",
                    "LoadBearing",
                    "FireRating"]
        case "Slab":
            items = [
                    "Status",
                    "AcousticRating",
                    "FireRating",
                    "PitchAngle",
                    "Combustible",
                    "SurfaceSpreadOfFlame",
                    "Compartmentation",
                    "isExternal",
                    "ThermalTransmittance",
                    "LoadBearing"]
        case "Stair":
            items = [
                    "Status",
                    "NumberOfRiser",
                    "NumberOfTreads",
                    "RiserHeight",
                    "TreadLength",
                    "NosingLength",
                    "WalkingLineOffset",
                    "TreadLengthAtOffset",
                    "TreadLengthAtInnerSide",
                    "WaistThickness",
                    "RequiredHeadroom",
                    "HandicapAccessible",
                    "HasNonSkidSurface",
                    "IsExternal",
                    "ThermalTransmittance",
                    "LoadBearing",
                    "FireRating",
                    "FireExit"]          
        case "Wall":
            items = [
                    "Status",
                    "AcousticRating",
                    "FireRating",
                    "Combustible",
                    "SurfaceSpreafOfFlame",
                    "ThermalTransmittance",
                    "IsExternal",
                    "LoadBearing",
                    "ExtendToStructure",
                    "Compartmentation"]
        case "Window":
            items = [
                    "Status",
                    "AcousticRating",
                    "FireRating",
                    "SecurityRating",
                    "IsExternal",
                    "Infiltration",
                    "ThermalTransmittance",
                    "GlazingAreaFraction",
                    "HasSillExternal",
                    "HasSillInternal",
                    "HasDrive",
                    "SmokeStop",
                    "FireExit",
                    "WaterTightnessRating",
                    "MechanicalLoadRating",
                    "WindLoadRating"]
    return items            