import xlsxwriter
import os

class ExportTool:
    def export_books_to_excel(self, filename, books):
        """Xuất danh sách sách ra file Excel với định dạng chính xác."""
        if not books:
            print("Danh sách sách rỗng, không thể xuất file.")
            return False  # Trả về False nếu không có dữ liệu

        try:
            # Tạo workbook và worksheet
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet()

            # Cài đặt độ rộng cột
            worksheet.set_column('A:A', 15)  # Book ID
            worksheet.set_column('B:B', 30)  # Book Name
            worksheet.set_column('C:C', 20)  # Author
            worksheet.set_column('D:D', 15)  # PubYear
            worksheet.set_column('E:E', 12)  # Quantity

            # Định dạng tiêu đề (header)
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#DCE6F1',
                'border': 1
            })

            # Định dạng văn bản (text)
            text_format = workbook.add_format({'align': 'left', 'border': 1})

            # Định dạng số (number)
            number_format = workbook.add_format({'num_format': '0', 'align': 'center', 'border': 1})

            # Thêm tiêu đề
            headers = ['Book ID', 'Book Name', 'Author', 'PubYear', 'Quantity']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)  # Ghi tiêu đề

            # Ghi dữ liệu vào từng dòng
            for i, book in enumerate(books, start=1):
                worksheet.write(i, 0, book.book_id, number_format)
                worksheet.write(i, 1, book.title, text_format)
                worksheet.write(i, 2, book.author, text_format)
                worksheet.write(i, 3, book.publication_year, number_format)
                worksheet.write(i, 4, book.quantity, number_format)

            # Đóng file Excel
            workbook.close()
            print(f"File {filename} đã được lưu tại: {os.path.abspath(filename)}")
            return True  # Xuất file thành công

        except Exception as e:
            print(f"Lỗi khi xuất file: {e}")
            return False  # Xuất file thất bại
