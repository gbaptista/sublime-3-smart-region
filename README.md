# Smart Region

Open and search files directly from your source code.

![Demo: Smart Region](https://raw.githubusercontent.com/gbaptista/sublime-3-smart-region/master/demo.gif)

### Command Palette

Smart Region: Open `smart_region_open`

Smart Region: Create Regions `smart_region_create_regions`

### Default Shortcuts
* Open with keyboard: _ctrl + enter_
* Open with mouse: _ctrl + double click_

### Settings

`User/Preferences.sublime-settings`:
```javascript
"smart_region_create_regions_on": ["load", "modified"],

// Draw Regions Options:
// draw_empty, hide_on_minimap, draw_empty_as_overwrite, draw_no_fill
// draw_no_outline, draw_solid_underline, draw_stippled_underline
// draw_squiggly_underline, persistent, hidden
// Suggested combinations:
//
//   ["hide_on_minimap", "draw_no_fill", "draw_no_outline", "draw_stippled_underline"]
//
//   ["hide_on_minimap", "draw_no_fill", "draw_no_outline", "draw_solid_underline"]
//
//   ["hide_on_minimap", "hidden"]
//
"smart_region_draw_regions": ["hide_on_minimap", "draw_no_fill", "draw_no_outline", "draw_solid_underline"],

"smart_region_debug": false
```

### Custom Shortcuts
`User/Default.sublime-keymap`:
```javascript
{ "keys": ["ctrl+enter"], "command": "smart_region_open" }
```

`User/Default.sublime-mousemap`:
```javascript
{
  "button": "button1", "count": 2, "modifiers": ["ctrl"],
  "press_command": "drag_select",
  "command": "smart_region_open"
}
```

### To-Do
* Windows support.
* URL's support.
* Improve performance for large files.
