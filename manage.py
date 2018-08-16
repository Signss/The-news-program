from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import db, create_app


# # 创建flask 实例对象
app = create_app('dev')
manager = Manager(app)
# 使迁移时app和db产生关联
Migrate(app, db)
# 向终端关联对象中添加迁移命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
