from aiogram import executor

from create import disp
from handlers import downloads, start, profile
from handlers.handlers_admin import admin
from handlers.handlers_admin.handlers_admin_admin_list import admin_add, admin_remove, admin_list
from handlers.handlers_admin.handlers_admin_content import trigger, admin_content, admin_actual

admin.reg_admin(disp)
admin_list.reg_admin_list(disp)
admin_add.reg_admin_add(disp)
admin_remove.reg_admin_remove(disp)
admin_content.reg_admin_content(disp)
admin_actual.reg_admin_actual(disp)
trigger.reg_admin_trigger(disp)

profile.reg_profile(disp)
start.reg_start(disp)
downloads.reg_downloads(disp)
executor.start_polling(disp, skip_updates=True)
