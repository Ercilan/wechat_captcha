# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/16 14:44
import os
import re
import shutil
import tkinter as tk
import traceback
import webbrowser
from tkinter import ttk, filedialog

from PIL import Image, ImageTk

VER = "1.0"
TIPS = """Enter/下一张：【自动保存重命名】、显示下一张图片
↑、↓方向键：聚焦到历史记录，选中需要的条目后，空格键/鼠标双击，自动保存重命名、下一张
Shift + Enter：返回上一张图片
Ctrl + Z：恢复file_name中的word到输入框
Esc：聚焦到输入框
"""
README = """需要图片名称中包含数字、字符，程序正则匹配该数字进行排序，以该字符作为待评估的字符待人工校验。
目前正则是写死在代码里的...有需要自行修改

 - 一般是图片是序号开头，便于资源管理器排序，利于查找"""


def get_files_by_name(path, name_reg: str = r"(\d+)\.jpeg"):
    """
    根据名称里的序号增序排序文件
    """
    files = os.listdir(path)
    # files.sort(key=lambda x: int(re.search(name_reg, x)[1]))
    # 获取目标文件夹中所有文件的路径
    file_paths = [os.path.join(path, filename) for filename in os.listdir(path)]

    # 根据文件的最后修改时间进行排序
    sorted_files = sorted(file_paths, key=lambda x: os.path.getmtime(x))
    return sorted_files


def get_word_from_path(path):
    return re.search(r"(.*?)\.jpeg", path)[1]


def choose_folder(img_labeler):
    folder_path = filedialog.askdirectory(initialdir=os.getcwd())
    if folder_path:
        img_labeler.load_content(folder_path)
        img_labeler.status_var.set("")


class ImageLabeler:
    def __init__(self, root, image_folder, zoom_factor: int = 3,
                 limit_input_length: int = 1, limit_submit_length: int = 1):
        self.root = root
        self.image_folder = image_folder
        self.zoom_factor = zoom_factor
        self.image_paths = None
        self.current_index = None
        self.words = None
        self.origin_pic_name = None
        self.new_name = None
        self.limit_input_length = limit_input_length
        self.limit_submit_length = limit_submit_length

        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, padx=0, pady=0, fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(self.left_frame)
        self.image_label.pack(side=tk.LEFT, padx=10, pady=10)
        border = ttk.Separator(root, orient="vertical")
        border.pack(in_=self.left_frame, side="right", fill="y")

        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, padx=0, pady=0, fill=tk.Y)

        border = ttk.Separator(root, orient="vertical")
        border.pack(in_=self.right_frame, side="left", fill="y")

        self.scrollbar = tk.Scrollbar(self.right_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_desc_label = tk.Label(self.right_frame, text="已出现过的字符", justify=tk.LEFT)
        self.history_desc_label.pack(padx=1, pady=0)
        self.history_listbox = tk.Listbox(self.right_frame, yscrollcommand=self.scrollbar.set,
                                          font=('Microsoft YaHei', 13), activestyle="dotbox", cursor="hand2")

        self.scrollbar.config(command=self.history_listbox.yview)

        self.history_listbox.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.history_listbox.bind("<Double-Button-1>", self.fill_input_from_history(need_next=True))
        self.history_listbox.bind("<space>", self.fill_input_from_history(need_next=True, change_input_entry=False))

        self.image_name_var = tk.StringVar()
        image_name_label = tk.Label(root, textvariable=self.image_name_var, font=('Microsoft YaHei', 14), width=20)
        image_name_label.pack(pady=10)
        self.input_entry = tk.Entry(root, width=10, validate='key')
        # 允许输入一个词组，方便打字；后面限制只能输入一个字符
        self.input_entry['validatecommand'] = (
            self.input_entry.register(lambda v: len(v) <= self.limit_input_length), '%P')
        self.input_entry.config(font=('Microsoft YaHei', 16))
        self.input_entry.pack(pady=10)
        self.input_entry.bind('<KeyRelease>', self.update_label)

        self.next_button = tk.Button(root, text="下一张", command=self.next_image)
        self.next_button.config(font=('Microsoft YaHei', 17))
        self.next_button.pack(pady=10)

        self.pre_button = tk.Button(root, text="上一张", command=self.pre_image)
        self.pre_button.config(font=('Microsoft YaHei', 17))
        self.pre_button.pack(pady=10)


        self.next_button = tk.Button(root, text="转移", command=self.transform)
        self.next_button.config(font=('Microsoft YaHei', 17))
        self.next_button.pack(pady=10)

        self.status_var = tk.StringVar()
        status_label = tk.Label(root, textvariable=self.status_var, justify=tk.LEFT, fg="blue",
                                font=("Microsoft YaHei", 12))
        status_label.pack(padx=10, pady=10)

        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(side=tk.BOTTOM, padx=0, pady=0)
        border = ttk.Separator(root, orient="horizontal")
        border.pack(in_=self.bottom_frame, fill="x")
        tips_label = tk.Label(self.bottom_frame, text=TIPS, justify=tk.LEFT)
        tips_label.pack(padx=10, pady=10)

        self.root.bind('<Escape>', lambda e: self.input_entry.focus_set())
        self.root.bind('<Return>', self.next_image)
        self.root.bind("<Shift-Return>", self.pre_image)
        self.root.bind("<Control-z>", self.undo)

        root.bind("<Up>", self.on_up)
        root.bind("<Down>", self.on_down)
        self.base_title = None
        self.load_content(image_folder, zoom_factor)

    def load_content(self, image_folder, zoom_factor: int = 3):
        self.image_folder = image_folder
        self.zoom_factor = zoom_factor
        title = f"字符图片标注工具 - v{VER}"
        if image_folder:
            self.base_title = f"{title} - [{os.path.abspath(image_folder)}]"
            self.root.title(self.base_title)
        else:
            self.base_title = title
            self.root.title(self.base_title)
            self.status_var.set("程序已就绪")
            return
        try:
            self.image_paths = [os.path.join(self.image_folder, filename) for filename in
                                get_files_by_name(self.image_folder, name_reg=r"(\d+)-.*?\.jpeg")]
        except Exception as e:
            show_error_popup(self.root, "遍历目标文件夹出现异常，请检查排序正则是否正确、文件夹是否正确等")
            return
        self.current_index = 0
        self.words = {}

        self.origin_pic_name = None
        self.new_name = None
        self.history_listbox.delete(0, tk.END)
        if len(self.image_paths) > 0:
            self.show_next_image()

    def on_up(self, event):
        self.history_listbox.focus_set()
        selected_index = self.history_listbox.curselection()
        if not selected_index:
            self.history_listbox.select_set(0)

    def on_down(self, event):
        self.history_listbox.focus_set()
        selected_index = self.history_listbox.curselection()
        if not selected_index:
            self.history_listbox.select_set(0)

    def show_next_image(self):
        if self.current_index < len(self.image_paths):
            self.next_button.config(state=tk.NORMAL)
            image_path = self.image_paths[self.current_index]
            self.current_index += 1
            self.root.title(
                f"{self.base_title} - [{self.current_index}/{len(self.image_paths)}]"
            )
            # 倒数第一个
            if self.current_index >= len(self.image_paths):
                # 允许显示，让用户可以点击按钮保存
                self.status_var.set("已遍历完成，没有下一张了！")

            if 1 < self.current_index:
                self.pre_button.config(state=tk.NORMAL)
            else:
                self.pre_button.config(state=tk.DISABLED)

            pil_image = Image.open(image_path)
            new_width = int(pil_image.width * self.zoom_factor)
            new_height = int(pil_image.height * self.zoom_factor)
            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

            word = get_word_from_path(os.path.basename(image_path))
            self.image_label.config(image=photo)
            self.image_label.image = photo

            self.origin_pic_name = os.path.basename(image_path)
            self.new_name = self.origin_pic_name
            print(f"--> {self.origin_pic_name}")
            self.image_name_var.set(self.origin_pic_name)
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, word)
            self.input_entry.focus()
        else:
            image_path = self.image_paths[self.current_index - 1]
            self.origin_pic_name = os.path.basename(image_path)
            self.image_name_var.set(self.origin_pic_name)
            self.next_button.config(state=tk.DISABLED)

    def set_new_name(self, input_word):
        # self.new_name = re.sub(r"^(?P<pre>\d+-\d+-\d+-)(.*)(?P<suf>\.jpeg)$", r"\g<pre>" +
        self.new_name = re.sub(r"^(.*)\.jpeg$", input_word + ".jpeg", self.origin_pic_name)

    def update_label(self, event=None):
        self.set_new_name(self.input_entry.get().strip())
        self.image_name_var.set(self.new_name)

    def undo(self, event=None):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, get_word_from_path(self.image_paths[self.current_index - 1]))

    def fill_input_from_history(self, need_next: bool, change_input_entry: bool = True):
        def wrapper(event):
            if self.history_listbox.size() == 0:
                return

            selected_item: str = self.history_listbox.get(self.history_listbox.curselection())
            dash_index = selected_item.index(" - ")
            # bracket_index = selected_item.index("\t[")
            # word = selected_item[dash_index + 3:bracket_index]
            word = selected_item[dash_index + 3:]
            print(f"<-- {word}")

            if self.current_index >= len(self.image_paths) or change_input_entry:
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, word)
            if need_next:
                self.set_new_name(word)
                self.next_image(check_input_entry=False)

        return wrapper

    def pre_image(self, event=None):
        self.status_var.set("")
        if self.current_index > 1:
            # 舍弃当前的输入
            self.current_index -= 2
            self.show_next_image()

    def get_word_show(self, user_input):
        # todo 计数需要增减计数、条目增删，比较麻烦。意义不是很大，后续会清理
        # return f"{len(self.words)} - {user_input}\t[{self.words[user_input]}]"
        return f"{len(self.words)} - {user_input}"

    def transform(self, *args, **kwargs):
        self.next_image(*args, **kwargs)
        image_path = self.image_paths[self.current_index - 2]
        # print(image_path)
        shutil.move(image_path, "failed")

    def next_image(self, event=None, check_input_entry: bool = True):
        user_input = self.input_entry.get()
        # 限死长度只能为1
        if check_input_entry:
            if user_input and len(user_input.strip()) == self.limit_submit_length:
                self.status_var.set("")
                user_input = user_input.strip()
                print(f"<-- {user_input}")
                if user_input in self.words:
                    self.words[user_input] += 1
                else:
                    self.words[user_input] = 1
                    self.history_listbox.insert(tk.END, self.get_word_show(user_input))
            else:
                self.status_var.set("输入不合法！！！")
                return
        name_changed = self.new_name is not None and self.new_name != self.origin_pic_name
        if name_changed and (check_input_entry and len(user_input.strip()) == self.limit_submit_length or not check_input_entry):
            print(f"{self.origin_pic_name}  -->  {self.new_name}")
            dst = f"{self.image_folder}/{self.new_name}"
            try:
                os.rename(f"{self.image_folder}/{self.origin_pic_name}", dst)
            except Exception as e:
                show_error_popup(self.root,
                                 f"重命名发生异常，请检查：{self.image_folder}/{self.origin_pic_name} --> {dst}")
                return

            print(f"重命名完成！")
            self.image_paths[self.current_index - 1] = dst
        self.show_next_image()


def show_error_popup(root, error_message):
    popup = tk.Toplevel(root)
    popup.title("发生错误")

    text_widget = tk.Text(popup)
    text_widget.pack(fill=tk.BOTH, expand=True)

    error_stack_trace = traceback.format_exc()
    text_widget.insert(tk.END, error_message + f"\n\n{'=' * 75}\n\n")
    text_widget.insert(tk.END, error_stack_trace)


def show_about_popup(root):
    popup = tk.Toplevel(root)
    popup.title("关于")

    label = tk.Label(popup, text=README, wraplength=270, justify=tk.LEFT)
    label.pack(padx=10, pady=10)

    ok_button = tk.Button(popup, text="OK", width=5, command=popup.destroy)
    ok_button.pack(padx=10, pady=20)
    popup_width = 300
    popup_height = 170
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - popup_width) // 2
    y = (screen_height - popup_height) // 2
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")


def show_readme_popup(root):
    popup = tk.Toplevel(root)
    popup.title("使用说明")

    label = tk.Label(popup, text="一个简易的字符图片标注工具")
    label.pack(padx=10, pady=10)

    link_label = tk.Label(popup, text="http://ercilan.cn", fg="blue", cursor="hand2")
    link_label.pack(padx=10, pady=10)
    link_label.bind("<Button-1>", lambda e: webbrowser.open("http://ercilan.cn"))

    ok_button = tk.Button(popup, text="OK", width=5, command=popup.destroy)
    ok_button.pack(padx=10, pady=20)
    popup_width = 300
    popup_height = 170
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - popup_width) // 2
    y = (screen_height - popup_height) // 2
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")


def main(image_folder=None):
    labeler = None
    root = tk.Tk()
    # 图片太大这里取消禁止全屏，一般字符图片不会很大。主要是这布局方式全屏难看
    # root.resizable(False, False)

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(menu=file_menu, label="文件")
    file_menu.add_command(label="打开目录", command=lambda: choose_folder(labeler))
    file_menu.add_command(label="退出", command=root.destroy)

    about_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="关于", menu=about_menu)
    about_menu.add_command(label="关于", command=lambda: show_readme_popup(root))
    about_menu.add_command(label="使用说明", command=lambda: show_about_popup(root))

    labeler = ImageLabeler(root, image_folder, zoom_factor=3, limit_input_length=6, limit_submit_length=6)

    root.mainloop()


if __name__ == "__main__":
    # https://github.com/Ercilan/character_correction
    main()
