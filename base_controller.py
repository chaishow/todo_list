import json
import uuid


class Task:
    def __init__(self, task, done=False, id=None):
        self.task = task
        self.done = done
        if not id:
            self.id = id or uuid.uuid4().hex
        else:
            self.id = id

    @classmethod
    def init_from_json(cls, string):
        data = json.loads(string)
        id, task, done = (data.get('id', None),
                          data.get('task', None),
                          data.get('done', None))

        return cls(id=id, task=task, done=done)

    def get_id(self):
        return self.id

    def change_status(self):
        self.done = not self.done

    def json(self):
        return json.dumps(self.__dict__).encode('utf-8')

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return f'{self.id} {self.task} {self.done}'

    def __repr__(self):
        return f'{self.id} {self.task} {self.done}'


class TaskList(list):
    def find_by_id(self, id):
        for task in self:
            if task.get_id() == id:
                return task
        raise KeyError('Задачи с таким id не существует')


class TaskBase:
    def __init__(self, path: str) -> None:
        self.path = path

    def __load_tasks(self):
        try:
            with open(self.path, mode='r', encoding='utf-8') as base:
                return TaskList([Task.init_from_json(line) for line in base])
        except FileNotFoundError:
            return TaskList()

    def __save_tasks(self, task_list):
        try:
            with open(self.path, mode='w', encoding='utf-8') as base:
                for task in task_list:
                    base.write(task.json().decode()+'\n')
        except FileNotFoundError:
            print('Файл базы данных не найден')

    def append_task(self, task: str | Task) -> None:
        try:
            with open(self.path, mode='a', encoding='utf-8') as base:
                if isinstance(task, str):
                    task = Task(task)
                base.write(task.json().decode()+'\n')
        except FileNotFoundError:
            print('Файл базы данных не найден')

    def json(self, as_bytes=False):
        result = json.dumps([task.__dict__ for task in self.__load_tasks()])
        return result.encode('utf-8') if as_bytes else result

    def delete_by_id(self, id):
        new_tasks = [task for task in self.__load_tasks()
                     if task.get_id() != id]
        if len(new_tasks) == len(self.__load_tasks()):
            raise KeyError('Задачи с таким id не существует')
        self.__save_tasks(new_tasks)

    def change_status_by_id(self, id):
        task_list = self.__load_tasks()
        task_list.find_by_id(id).change_status()
        self.__save_tasks(task_list)

    def clear_all(self):
        self.__save_tasks(TaskList())
