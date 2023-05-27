# from mobi import Mobi
import os

import ebooklib
import mobi
from bs4 import BeautifulSoup
from ebooklib import epub
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


class Chapter(object):

    # 初始化
    def __init__(self, name, text):
        self.Name = name
        self.Text = text

    # 输出章节信息
    def print_info(self):
        print("章节名称：")
        print(self.Name)
        print("章节内容：")
        print(self.Text)


class FileChangeSys(object):

    # 初始化
    def __init__(self, path):
        self.Path = path
        self.Chapter_uniform = []
        self.Name = None
        self.dot_index = None
        self.Type = None

    # 解码Path
    def decode_filetype(self):
        self.Name = os.path.basename(self.Path)
        self.dot_index = self.Name.find('.')
        self.Type = self.Name[self.dot_index + 1:]

    # print文件信息
    def print_fileinfo(self):
        print("Filepath:")
        print(self.Path)
        print("Filename:")
        print(self.Name)
        print("Filetype:")
        print(self.Type)

    # 如果是pdf类型，直接终端输出
    def pdf_decode(self):
        # 获取文档
        fp = open(self.Path, 'rb')
        # 创建解释器
        pdf_parser = PDFParser(fp)
        # PDF文档对象
        doc = PDFDocument(pdf_parser)
        # 连接解释器和文档对象
        pdf_parser.set_document(doc)
        # doc.set_parser(pdf_parser)

        # 初始化文档
        # doc.initialize()

        # 创建PDF资源管理器
        resource = PDFResourceManager()
        # 创建一个PDF参数分析器
        laparam = LAParams()
        # 创建聚合器
        device = PDFPageAggregator(resource, laparams=laparam)
        # 创建PDF页面解析器
        interpreter = PDFPageInterpreter(resource, device)
        # 循环遍历列表，每次处理一页的内容
        # doc.get_pages() 获取page列表
        page_index = 0  # 统计页数
        for page in PDFPage.create_pages(doc):
            # 使用页面解释器来读取
            page_index += 1
            new_chapter_name = "第" + str(page_index) + "页"
            interpreter.process_page(page)
            # 使用聚合器获得内容
            new_chapter_text = ""
            layout = device.get_result()
            for out in layout:
                if hasattr(out, 'get_text'):
                    new_chapter_text += out.get_text()
            new_chapter = Chapter(new_chapter_name, new_chapter_text)
            self.Chapter_uniform.append(new_chapter)
            new_chapter.print_info()

    # txt文档转pdf文档
    def txt_decode(self):
        # 暂时：章节名就是书名
        new_chapter_name = self.Name
        f = open(self.Path, 'r')
        new_chapter_text = f.read()
        # print(new_chapter_text)

        # 合成一个章节
        new_chapter = Chapter(new_chapter_name, new_chapter_text)

        self.Chapter_uniform.append(new_chapter)

        new_chapter.print_info()

    # epub转pdf
    def epub_decode(self):
        """
        path_dot=self.Path.find('.epub')
        html_path=self.Path[:path_dot]+'.html'
        changepub=epub2html.Epub2Html(self.Path,html_path)
        changepub.gen()
        text_uniform_path=html_path+'/'+self.Path[:path_dot]+'/OEBPS/Text'
        text_uniform_dir=os.listdir(text_uniform_path)
        for c in text_uniform_dir:
            #获取章节名称
            new_chapter_name=c[:c.find('.xhtml')]
            #获取章节内容
            f=open(text_uniform_path+'/'+c,'r',encoding = 'utf-8')
            xhtml=f.read()
            soup=BeautifulSoup(xhtml,'lxml')
            #print(soup)
            new_chapter_text=''
            for item in soup.find_all("p"):
                #print(item.text)
                new_chapter_text+=item.text
                new_chapter_text+='\n'
            if new_chapter_text.isspace():
                new_chapter_text="该章节可能仅由图片构成"
        
            #整合成章节类
            new_chapter=Chapter(new_chapter_name,new_chapter_text)
            #加入list
            self.Chapter_uniform.append(new_chapter)
            #print下信息
            new_chapter.print_info()
        """
        book = epub.read_epub(self.Path)

        index = 0

        for text in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            index += 1
            soup = BeautifulSoup(text.get_content(), 'html')
            new_chapter_text = ''
            for item in soup.find_all("p"):
                # print(item.text)
                new_chapter_text += item.text
                new_chapter_text += '\n'
            if new_chapter_text.isspace():
                new_chapter_text = "该章节可能仅由图片构成"

            new_chapter_name = "第" + str(index) + "章"

            # 整合成章节类
            new_chapter = Chapter(new_chapter_name, new_chapter_text)
            # 加入list
            self.Chapter_uniform.append(new_chapter)
            # print下信息
            new_chapter.print_info()

    # mobi转pdf
    def mobi_decode(self):
        """
        path_dot=self.Path.find('.mobi')
        new_pdf_path=self.Path[:path_dot]+'.pdf'
        tempdir, filepath = mobi.extract(self.Path)
        pypandoc.convert_file(filepath,'pdf',outputfile=new_pdf_path,extra_args=['--latex-engine=xelatex'])
        self.printPDF(new_pdf_path)
        """
        tempdir, filepath = mobi.extract(self.Path)
        print(filepath)
        new_chapter_name = self.Name
        # 获取章节内容
        f = open(filepath, 'r', encoding='utf-8')
        html = f.read()
        soup = BeautifulSoup(html, 'lxml')
        # print(soup)
        new_chapter_text = ''
        for item in soup.find_all("p"):
            # print(item.text)
            new_chapter_text += item.text
            new_chapter_text += '\n'
        if new_chapter_text.isspace():
            new_chapter_text = "该章节可能仅由图片构成"

        # 整合成章节类
        new_chapter = Chapter(new_chapter_name, new_chapter_text)
        # 加入list
        self.Chapter_uniform.append(new_chapter)
        # print下信息
        new_chapter.print_info()


"""        
f=FileChangeSys("不能承受的生命之轻 (米兰·昆德拉).epub")
f.decodeFileType()
#f.printFileinfo()  
f.epub_decode()
"""
