class TaskUtil:
  def __init__(self):
    pass
  
  def generate_user_name(self, full_name):
      full_name = full_name.replace(".", "")
      full_name = full_name.replace("#", "")
      full_name = full_name.replace("_", "")
      full_name = full_name.replace("-", "")
      full_name = full_name.replace("!", "")
      if full_name == "":
          return ""
      else:
          full_name_list = full_name.split(" ")	
          if len(full_name_list) > 1:
              user_name = full_name_list[0][0] + full_name_list[-1]
          else:
              user_name = full_name_list[0]
  
      return user_name[0:64].lower()
