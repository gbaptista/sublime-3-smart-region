import sublime, sublime_plugin, os, re, time

class SmartRegionOpen(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    if SmartRegion.get_setting("debug"):
      sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
      print('>>>>>>>>>>>>>>>>>>> SmartRegionOpen Debug:')

    target = SmartRegion.get_target(self.view, args)

    if not target:
      return False

    line = False

    if re.search(':', target):
      target, line = target.split(':')

    if SmartRegion.get_setting("debug"):
      print('target:', target)
      print('line:', line)

    if target:
      if(os.path.isfile(target)):
        self.open_file(target, line)
      else:
        founded_files = []
        first_root = False
        if self.view.window() and self.view.window().project_data():
          for folder in self.view.window().project_data()['folders']:
            for root, dirs, files in os.walk(folder["path"]):
              # [TODO] Needs a better strategy...
              if re.search(r"\.git([^i]|$)", root):
                next
              else:
                if not first_root:
                  first_root = root
                for file_name in files:
                  file_path = root + '/' + file_name
                  if re.search(target, file_name) or re.search(target, file_path):
                    if(os.path.isfile(file_name)):
                      founded_files.append(file_name)
                    elif(os.path.isfile(file_path)):
                      founded_files.append(file_path)

        if SmartRegion.get_setting("debug"):
          print('founded_files:')
          print(founded_files)

        reversed(founded_files)

        if len(founded_files) > 1:
          relative_path = target.replace(sublime.active_window().extract_variables()['folder'] + '/', '')
          self.view.window().run_command("show_overlay", {"overlay": "goto", "show_files": True, "text": relative_path})
          sublime.status_message('SmartRegion | Search for file.')
        elif len(founded_files) == 1:
          self.open_file(founded_files[0], line)
          sublime.status_message('SmartRegion | File opened.')
        else:
          sublime.status_message('SmartRegion | File not found: ' + target + ' | ' + first_root)

  def go_to_line(self, view, line):
    if not view.is_loading():
      line = int(line)

      if SmartRegion.get_setting("debug"):
        print('go to line: view loaded!')
        print('go to line:', line)

      view.sel().clear()
      view.sel().add(sublime.Region(view.text_point(line-1, 0)))
      view.show(view.text_point(line-1, 0))
    else:
      if SmartRegion.get_setting("debug"):
        print('go to line: view not loaded yet...')
      sublime.set_timeout(lambda: self.go_to_line(view, line), 10)

  def open_file(self, file, line):
    if SmartRegion.get_setting("debug"):
      print('open_file:', file)

    file_view = self.view.window().find_open_file(file)

    if file_view:
      if SmartRegion.get_setting("debug"):
        print('view exists:', 'focus')
      self.view.window().focus_view(file_view)
    else:
      if SmartRegion.get_setting("debug"):
        print('view not exists:', 'open')
      file_view = self.view.window().open_file(file)

    if line:
      self.go_to_line(file_view, line)

  def want_event(self):
    return True


class SmartRegionCreateRegions(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    SmartRegion.create_regions(self.view)

  def want_event(self):
    return True

class SmartRegion():
  def get_target(view, args):
    target = False
    sel_target = False

    if args.get("event"):
      click_text_position = view.window_to_text((args["event"]["x"], args["event"]["y"]))
    else:
      sel_target = view.substr(view.sel()[0])
      click_text_position = view.sel()[0].begin()

    for region in view.get_regions('smart_region'):
      if region.contains(click_text_position):
        target = view.substr(region)

    if not target:
      target = sel_target

    if not target:
      sublime.status_message('SmartRegion | No Target')
    else:
      return target

  def create_regions(view):
    if view.size() > 100000:
      sublime.status_message('SmartRegion | File is too large: ' + str(view.size()) + ' chars')
    else:
      regions = []

      if view.window() and view.window().project_data():
        for folder in view.window().project_data()['folders']:
          for root, dirs, files in os.walk(folder["path"]):

            # [TODO] Needs a better strategy...
            if re.search(r"\.git([^i]|$)", root):
              next
            else:
              for target in view.find_all(re.escape(root)):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

              for target in view.find_all(re.escape(root) + ':\d{1,}'):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

              # [TODO] Maybe this is not a good idea...
              for dir_name in dirs:
                for target in view.find_all(re.escape(dir_name)):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

                for target in view.find_all(re.escape(dir_name) + ':\d{1,}'):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

              for file_name in files:
                full_path = root + '/' + file_name
                relative_path = full_path.replace(sublime.active_window().extract_variables()['folder'] + '/', '')

                for target in view.find_all(re.escape(file_name)):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

                for target in view.find_all(re.escape(file_name) + ':\d{1,}'):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

                for target in view.find_all(re.escape(relative_path)):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

                for target in view.find_all(re.escape(relative_path) + ':\d{1,}'):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

                for target in view.find_all(re.escape(full_path)):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

                for target in view.find_all(re.escape(full_path) + ':\d{1,}'):
                  regions.append(view.find(re.escape(view.substr(target).strip()), target.begin()))

      file_regex = "((\s\/|^\/)[\w|\-|\/|\@|\.]{1,}[\.[\w|\-]{1,}|$])"

      for target in view.find_all(file_regex):
        regions.append(view.find(view.substr(target).strip(), target.begin()))

      for target in view.find_all(file_regex + ':\d{1,}'):
        regions.append(view.find(view.substr(target).strip(), target.begin()))

      flags = 0

      if "draw_empty" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.DRAW_EMPTY

      if "hide_on_minimap" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.HIDE_ON_MINIMAP

      if "draw_empty_as_overwrite" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.DRAW_EMPTY_AS_OVERWRITE

      if "draw_no_fill" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.DRAW_NO_FILL

      if "draw_no_outline" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.DRAW_NO_OUTLINE

      if "draw_solid_underline" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.DRAW_SOLID_UNDERLINE

      if "draw_stippled_underline" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.DRAW_STIPPLED_UNDERLINE

      if "draw_squiggly_underline" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.DRAW_SQUIGGLY_UNDERLINE

      if "persistent" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.PERSISTENT

      if "hidden" in SmartRegion.get_setting("draw_regions"):
        flags += sublime.HIDDEN

      view.add_regions('smart_region', regions, 'code', '', flags)

  def get_setting(config):
    settings = sublime.load_settings('Preferences.sublime-settings')
    if settings.get('smart_region_' + config):
      return settings.get('smart_region_' + config)
    else:
      settings = sublime.load_settings('SmartRegion.sublime-settings')
      return settings.get('smart_region_' + config)

class KeyBindingListener(sublime_plugin.EventListener):

  def on_load_async(self, view):
    if "load" in SmartRegion.get_setting("create_regions_on"):
      SmartRegion.create_regions(view)

  def on_modified_async(self, view):
    if "modified" in SmartRegion.get_setting("create_regions_on"):
      SmartRegion.create_regions(view)

