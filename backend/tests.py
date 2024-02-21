from django.test import TestCase

# Create your tests here.
# @login_required(login_url='login')
# def add_income_docu(request):
#     docutypes = DocumentType.objects.filter(status=True)
#     levels = DocumentLevel.objects.all()
#     status = ProcessStatus.objects.all()
#     title = "Thêm văn bản mẫu"

#     if request.method == 'POST':
#         issuing_agency = request.POST.get('issuing_agency')
#         responsible_agency = request.POST.get('responsible_agency')
#         reference_number = request.POST.get('reference_number')
#         level_id = request.POST.get('level')  # Assume 'level' is the ID of the DocumentLevel
#         document_type_id = request.POST.get('document_type')  # Assume 'document_type' is the ID of the DocumentType
#         receipt_date = request.POST.get('receipt_date')
#         issuance_date = request.POST.get('issuance_date')
#         current_number = request.POST.get('current_number')
#         arrival_number = request.POST.get('arrival_number')
#         summary = request.POST.get('summary')
#         advisory_opinions = request.POST.get('advisory_opinions')
#         publish = request.POST.get('publish')
#         status_id = request.POST.get('status')  # Assume 'status' is the ID of the ProcessStatus
#         # Các trường khác tương tự

#         try:
#             level_instance = DocumentLevel.objects.get(pk=level_id)
#             document_type_instance = DocumentType.objects.get(pk=document_type_id)
#             status_instance = ProcessStatus.objects.get(pk=status_id)

#             income_docu = IncomingDocument.objects.create(
#                 issuing_agency=issuing_agency,
#                 responsible_agency=responsible_agency,
#                 reference_number=reference_number,
#                 level=level_instance,  # Assign the DocumentLevel instance
#                 document_type=document_type_instance,  # Assign the DocumentType instance
#                 receipt_date=receipt_date,
#                 issuance_date=issuance_date,
#                 current_number=current_number,
#                 arrival_number=arrival_number,
#                 summary=summary,
#                 advisory_opinions=advisory_opinions,
#                 publish = bool(int(publish)),
#                 status=status_instance  # Assign the ProcessStatus instance
#             )

#             files = request.FILES.getlist('uploadfile')
#             for file in files:
#                 upload_file = uploadFile(file=file)
#                 upload_file.save()
#                 income_docu.uploadfile.add(upload_file)

#             messages.success(request, 'Thêm mới văn bản đến thành công.')
#             return redirect('income_docu')
#         except Exception as e:
#             messages.error(request, 'Thêm mới văn bản đến thất bại.')
#             print(f"An error occurred: {e}")
#             messages.error(request, f"An error occurred: {e}")

#     return render(request, 'document/incomingdocument/add.html', {
#         'title': title,
#         'docutypes': docutypes,
#         'levels': levels,
#         'status': status
#     })




# def add_user(request):
#     error_messages = []
#     if request.method == 'POST':
#         form = UserForm(request.POST, request.FILES)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             phone_number = form.cleaned_data['phone_number']  
#             # Check if email or phone number already exists
#             if User.objects.filter(email=email).exists():
#                 error_messages.append("Email đã tồn tại")
#             if User.objects.filter(phone_number=phone_number).exists():
#                 error_messages.append("Số điện thoại đã tồn tại")
            
#             if not error_messages:
#                 user = form.save(commit=False)
#                 user.status = True
#                 form.save()
#                 return redirect('user') # Redirect to a page where you list all positions
#         else:
#              # Collect all error messages into a list
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     error_messages.append(f"{error}")
#     else:
#         form = UserForm()
        
#     positions = Position.objects.all()
#     usercategories = UserCategory.objects.all()
#     departments = Department.objects.all()

#     context = {'form': form,
#                'positions': positions,
#                'usercategories': usercategories,
#                'departments':departments,
#                'error_messages':error_messages}
 
#     return render(request, 'account/user/add.html', context)


# def edit_user(request, user_id):
#     user = get_object_or_404(User, pk=user_id)
#     positions = Position.objects.all()
#     usercategories = UserCategory.objects.all()
#     departments = Department.objects.all()
#     error_messages = []

#     if request.method == 'POST':
#         form = UserForm(request.POST, request.FILES, instance=user)

#         try:
#             if form.is_valid():
#                 form.save()
#                 return redirect('user')
#             else:
#                 # Lấy tất cả các lỗi từ form.errors và thêm chúng vào error_messages
#                 for field_errors in form.errors.values():
#                     for error in field_errors:
#                         error_messages.append(error)

#         except ValidationError as e:
#             # Thêm thông báo lỗi từ ValidationError vào error_messages
#             error_messages.append(str(e))

#     else:
#         form = UserForm(instance=user)

#     context = {
#         'user': user,
#         'positions': positions,
#         'usercategories': usercategories,
#         'departments': departments,
#         'form': form,
#         'error_messages': error_messages  # Truyền error_messages vào context
#     }
#     return render(request, 'account/user/edit.html', context)


# def delete_user(request, user_id):
#     user = get_object_or_404(User, pk=user_id)
#     if request.method == 'POST':
#         user.delete()
#         # Chuyển hướng hoặc hiển thị thông báo thành công
#         return redirect('user')
#     # Hiển thị trang xác nhận xóa
#     context = {'user': user}
#     return render(request, 'account/user/delete.html', context)



    