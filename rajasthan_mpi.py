#!/usr/bin/env python
# coding: utf-8


import traceback
import sys
sys.path.append('C:/Users/HP/parse_unsearchable_rolls')

import os
import shutil
from PIL import Image,ImageDraw,ImageOps
import pytesseract
import re
import pandas as pd
import sys
from helper import *
import argparse

COLUMNS = ["id","electoral_name","father_or_husband_name","relationship","house_no","age","gender","address","main_town","district"]

state_name = "rajasthan"

PARSE_DATA_PAGES = os.path.join("parseData/images/",state_name)
create_path(PARSE_DATA_PAGES)

PARSE_DATA_BLOCKS = os.path.join("parseData/blocks/",state_name)
create_path(PARSE_DATA_BLOCKS)

PARSE_DATA_CSVS = os.path.join("parseData/csvs/",state_name)
create_path(PARSE_DATA_CSVS)

state_pdfs_path = None

def extract_first_page_details(path,input_images_blocks_path):
	
	img = Image.open(path)

	crop_path = os.path.join(os.path.join(input_images_blocks_path,"page"))
	create_path(crop_path)

	cropped_area = (2734,1871,3115,2410)
	crop_img = img.crop(cropped_area)
	crop_img = ImageOps.grayscale(crop_img)
	
	crop_det_path = os.path.join(crop_path,"det.jpg")
	crop_img.save(crop_det_path)
	# crop_img.close()

	text = (pytesseract.image_to_string(crop_img, config='--psm 4', lang='hin')) #config='--psm 4' config='-c preserve_interword_spaces=1'
	text = text.split('\n')
	text = [ i for i in text if i!='' and i!='\x0c']
	crop_img.close()

	main_town = text[0].strip() if len(text) >= 1 else ""
	police_station =text[1].strip() if len(text) >= 2 else ""
	revenue_division = text[2].strip() if len(text) >= 3 else ""
	mandal = text[3].strip() if len(text) >= 4 else ""
	district = text[4].strip() if len(text) >= 5 else ""
		
	return [main_town,police_station,revenue_division,mandal,district]

def generate_poll_blocks_from_page(page_full_path,page_blocks_path):
	
	img = Image.open(page_full_path)
	crop_width = 1253
	crop_height = 485

	def get_left_top(padding_x_list,padding_y_list,gap_x):
		top = None
		left = None

		found = False

		cur_x_offset = 0
		for _ in range(3):
			for l in padding_x_list:
				if found:
					continue
				for t in padding_y_list:
					start = l + cur_x_offset
					right = start + crop_width
					bottom = t + crop_height

					area = (start + 612,t,right - 10,t+100)
					cropped_img = img.crop(area)
					cropped_img = ImageOps.grayscale(cropped_img)

					cropped_img_data = pytesseract.image_to_string(cropped_img, config='--psm 6', lang='eng')
					cropped_img_data = cropped_img_data.replace("\n","").strip()

					if re.search("^[A-Za-z0-9/]*$",cropped_img_data):
						top = t
						left = l
						found = True
						break
			cur_x_offset += (gap_x + crop_width)

		return [left,top]
	
	def generate(left,top,gap_x,gap_y):
		count = 0
		l = left
		t = top

		for col in range(1,11):
			for row in range(1,4):
				right = l+crop_width
				bottom = t+crop_height
				area = (l, t, right, bottom)
				cropped_img = img.crop(area)
				count = count+1
				
				# new_area = (800,100, 1200, 470)
				region = Image.new("RGB", (crop_width, crop_height), (255,255,255))

				mask_image = Image.new("L",(crop_width,crop_height),255)
				draw = ImageDraw.Draw(mask_image)
				draw.rectangle((7,82,612,413),fill=0)

				cropped_img.paste(region,(0,0),mask_image)

				cropped_img = ImageOps.grayscale(cropped_img)
				
				cropped_img.save(os.path.join(page_blocks_path,str(count)+".jpg"),dpi=(300,300))
				cropped_img.close()

				cropped_img_id = img.crop((l+612,t,right-10,t+90))
				cropped_img_id = ImageOps.grayscale(cropped_img_id)

				cropped_img_id.save(os.path.join(page_blocks_path,"id_"+str(count)+".jpg"),dpi=(300,300))
				cropped_img_id.close()

				l = right + gap_x

			l = left
			t = t+crop_height+gap_y
	
	def get_address(left,top,right,bottom):
		area = (left,top,right,bottom)
		cropped_img = img.crop(area)

		cropped_img = ImageOps.grayscale(cropped_img)
		cropped_img.save(os.path.join(page_blocks_path,"0.jpg"),dpi=(300,300))
		cropped_img.close()

	padding_x = [170]
	padding_y = [287,347,475]

	gap_x = 4
	gap_y = 13

	[left,top] = get_left_top(padding_x,padding_y,gap_x)

	address_left = left
	address_top = 135
	address_right = 2930
	address_bottom = top

	if not left or not top:
		print(f"crop size is not valid")
		return

	if top != 475:
		get_address(address_left,address_top,address_right,address_bottom)

	if not left and not top:
		print("left and tip not found")
	else:
		print(f"left = {left} and top = {top}")

	if top == 475:
		gap_y = 37
	
	generate(left,top,gap_x,gap_y)

def extract_name(name):
	
	row = name.split(":")
	if len(row)!=2:
		return ""
	else:
		return row[1].strip()
	
def extract_vid(v_id):
	return v_id
	   

def extract_house_no(house_no):
	row = house_no.split(":")
	if len(row)==2:
		# house_no = re.findall(r'\d+', row[1].strip())
		house_no = row[1].strip()
		house_no = house_no.replace(" ","")
		if len(house_no)>0:
			return house_no
		else:
			return ""
	else:
		house_no = re.findall(r'\d+', row[0].strip())
		if len(house_no)>0:
			return house_no[0]
		else:
			return ""
	
def extract_age_gender(age_gender):
	row = age_gender.split(":")
	
	if len(row)!=3:
		return "",""
	else:    
		age = re.findall(r'\d+', row[1].strip())
		if len(age)>0:
			age =  age[0]
		else:
			age = ""
		
		if 'पुरूष' in row[2].strip() or 'पुरुष' in row[2].strip():
			# gender = 'पुरूष'
			gender = "male"
		elif 'स्त्री' in row[2].strip():
			# gender = 'स्त्री'
			gender = "female"
		else:
			gender =''

	return age, gender

def extract_rel_name(rel_name):
	row = rel_name.split(":")
	if len(row)!=2:
		
		row = rel_name.split(";")
		if len(row)!=2:
			return "",""
		else:
			rel_type = extract_rel_type(row[0].strip())
			return row[1].strip(),rel_type
	else:
		rel_type = extract_rel_type(row[0].strip())
		
		return row[1].strip(),rel_type
	
def extract_rel_type(rel_type):
	line = rel_type
	if line.startswith("पति") :
		rel_type = 'husband'
	elif line.startswith("पिता") or 'ता' in line :
		rel_type = 'father'
	elif line.startswith("माता") :
		rel_type = 'mother'
	elif line.startswith("अन्य") :
		rel_type = 'other'
	else:
		rel_type = ""
	
	return rel_type 

def extract_address(path):
	text = pytesseract.image_to_string(path, config='--psm 6', lang='hin').replace("\n","")
	text = text.split(":")

	text = [item.strip() for item in text if item.strip() != ""]

	if len(text) == 2:
		return text[1].strip()
	else:
		return ""

def extract_details_from_block(block):
	
	name = extract_name(block[0]) if len(block)>=1 else ""
	rel_name,rel_type = extract_rel_name(block[1]) if len(block)>=2 else ["",""]
	house_no = extract_house_no(block[2]) if len(block)>=3 else ""
	age,gender = extract_age_gender(block[3]) if len(block)>=4 else ["",""]
	v_id = extract_vid(block[4]) if len(block)>=5 else ""
	
	return [name,rel_name,rel_type,house_no,age,gender,v_id]

def run_tesseract(path):
	# text = (pytesseract.image_to_string(path, config='--psm 6', lang='eng+hin'))
	text_hin = (pytesseract.image_to_string(path, config='--psm 6', lang='hin'))
	text_eng = (pytesseract.image_to_string(path, config='--psm 6', lang='eng+hin'))

	file_name_without_ext = os.path.basename(path) 
	id_path = path.replace(file_name_without_ext,"id_"+file_name_without_ext)
	id_text = (pytesseract.image_to_string(id_path, config='--psm 6', lang='eng')).replace("\n","").strip()
	params_hin_list = text_hin.split('\n')
	params_eng_list = text_eng.split('\n')

	params_hin_list = [ i for i in params_hin_list if i!='' and i!='\x0c']
	params_eng_list = [ i for i in params_eng_list if i!='' and i!='\x0c']

	if len(params_eng_list)>2:
		params_hin_list[2] = params_eng_list[2]

	params_hin_list.append(id_text)

	return params_hin_list

def rename_filename(output_image_path,idx):
        path, filename = os.path.split(output_image_path)
        os.rename(output_image_path,path+"/"+str(idx)+".jpg")

def pdf_process(pdf_file_name):

	if not pdf_file_name.endswith(".pdf"):
		return
	
	print(f"processing {pdf_file_name}")

	try:
		#create images,blocks and csvs paths for each file
		pdf_file_name_without_ext = pdf_file_name.split('.pdf')[0]
		# input_pdf_images_path = PARSE_DATA_PAGES+pdf_file_name_without_ext+"/"
		input_pdf_images_path = os.path.join(PARSE_DATA_PAGES,pdf_file_name_without_ext)
		create_path(input_pdf_images_path)

		# input_images_blocks_path = PARSE_DATA_BLOCKS+pdf_file_name_without_ext+"/"
		input_images_blocks_path = os.path.join(PARSE_DATA_BLOCKS,pdf_file_name_without_ext)
		
		if os.path.exists(os.path.join(PARSE_DATA_CSVS,pdf_file_name_without_ext+".csv")):
			print(pdf_file_name_without_ext+".csv", "already exists")
			return
		
		try:
			if not os.path.exists(input_images_blocks_path):
				create_path(input_images_blocks_path)
				pdf_to_img(os.path.join(state_pdfs_path,pdf_file_name), input_pdf_images_path,dpi=500)
				input_images = os.listdir(input_pdf_images_path)

				for idx,input_image in enumerate(input_images,1):
					rename_filename(os.path.join(input_pdf_images_path,input_image),idx)
		except:
			traceback.print_exc()
			print(pdf_file_name_without_ext+".csv", "problem generating images from this pdf, must be empty or corrupted")
			return
		
		# sort pages for looping
		
		input_images = os.listdir(input_pdf_images_path)
	
		sort_nicely(input_images)
		
		#empty intial data
		df = pd.DataFrame(columns = COLUMNS)
		
		#for each page, parse the data
		for page in input_images:
		
			page_full_path = os.path.join(input_pdf_images_path,page)
			final_invidual_blocks = []

			page_no = int(page.replace(".jpg",""))
			
			#extract first page content
			if page == '1.jpg':
				# [main_town,police_station,revenue_division,mandal,district]
				first_page_list = extract_first_page_details(page_full_path,input_images_blocks_path)
				continue
				
			#ingnore 2nd page and last page
			if page == '2.jpg' or input_images[-1] == page:
				continue

			#loop from 3 page onwards
			if page.endswith('.jpg'):
				blocks_path = os.path.join(input_images_blocks_path,"blocks")
				create_path(blocks_path)

				page_idx = page.split(".jpg")[0]
				page_blocks_path = os.path.join(blocks_path,page_idx)
				create_path(page_blocks_path)
					
				generate_poll_blocks_from_page(page_full_path,page_blocks_path)
					
				sorted_blocks = os.listdir(page_blocks_path)
				sort_nicely(sorted_blocks)
				
				for jpg_file in sorted_blocks:

					if jpg_file.startswith("0"):
						address = extract_address(os.path.join(page_blocks_path,jpg_file))
						continue
					
					if jpg_file.startswith("id"):
						continue

					if jpg_file.endswith('.jpg'):
						new_params_list = run_tesseract(os.path.join(page_blocks_path,jpg_file))
						final_invidual_blocks.append(new_params_list)

			#put the data into dataframe
			# COLUMNS =   ["id","electoral_name","father_or_husband_name","relationship","house_no","age","gender","address","main_town","district"]
			for block in final_invidual_blocks:
				# [name,rel_name,rel_type,house_no,age,gender,v_id]
				block_list = extract_details_from_block(block)
				# name,rel_name,rel_type,house_no,age,gender,voter_id,number = block_list
				name,rel_name,rel_type,house_no,age,gender,v_id = block_list
				main_town = first_page_list[0]
				district = first_page_list[4]
				
				if name == "" or v_id == "":
					continue
							
				# final_list = arrange_columns(first_page_list,block_list,pdf_file_name_without_ext)
				final_list = [v_id,name,rel_name,rel_type,house_no,age,gender,address,main_town,district]
				# final_list.append(page_type)
				
				df_length = len(df)
				df.loc[df_length] = final_list
			
			print("page done : ",page)

					
		# save the dataframe(pdf) data into csv
		save_to_csv(df,os.path.join(PARSE_DATA_CSVS,pdf_file_name_without_ext+".csv"))
		print("CSV saved")
	
	except Exception as e:
		print('ERROR:', e, pdf_file_name_without_ext)
		traceback.print_exc()
	# finally:
	# 	print("Clean up working files...")
	# 	shutil.rmtree(input_pdf_images_path, ignore_errors=True)
	# 	shutil.rmtree(input_images_blocks_path, ignore_errors=True)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("--inputpdf",help = "path of the folder that contains pdf",required = True)
	args = parser.parse_args()

	state_pdfs_path = args.inputpdf
	state_pdf_files = os.listdir(state_pdfs_path)

	for state_pdf_file in state_pdf_files:
		pdf_process(state_pdf_file)

