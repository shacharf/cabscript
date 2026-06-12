# Goal

A web application for designing cabinets.

The design should be simple and easy and intuitive

## Requirements

### Inputs
- all units in mm
- Main material and width, assume we're using MDF or plywood boards.
  - Walls thickness
  - Doors thickness
  - Back thickness
  - Shelves thickness
- Type of closet: Cabinet-in-a-niche, kitchen-cabinet, standing-cabinet.
- Cabinet-dimensions: width x height x depth
- Niche-dimensions width x height x depth if applicable
- legs height
- Doors supported by concealed hinges
- Internal layout
  - Vertical splits / dividers / supports, height1, height2, position, at a single horizontal region, there may be more than one divider.
  - A simplified method to define bays, usage and repeat
    - usage: shelves, drawers, hanging, 
- Placement of shelves
- Dimensions of drawers - height, position
- shelve support method: Cleats, Shelf-Pins, fixed-screws.
- color palette: doors, shelves, cabinet.

Review the above list, anything to add?

## Method

- DSL language to descript a cabinet with minimal user input, include a standard library with common presets
- A UI do display the cabinet
- Export to standard formats
- Visual cabinet editor