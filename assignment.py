#-*- encoding:utf-8 -*-

import re
import sys

class Assignment:

	def extract(self, sentence, pattern):
		'''
		function：
			given sentence and regular expression, print matched substrings
		parameters:
			sentence: sentence to be matched
			pattern: regular expression
		'''

		reg = re.compile(pattern)
		result = reg.findall(sentence)[0][1]
		if result:
			print result


	def extractFile(self, filepath, patterns, outputfile):
		'''
		function:
			given the abstract file of knowledge graph, use regular expression
			to extract properties from abstract, and print the subject-property pair
			for every extracted property
		parameters:
			filepath: the path of abstract file
			pattern: regular expression
		'''
		
		#pattern = pattern.decode('utf-8')
		#reg = re.compile(pattern)

		wf = open(outputfile, 'w')
		with open(filepath, 'r') as f:
			for line in f.readlines():
				line = line.decode('utf-8')
				sentence = line.split('> \"')[1].split('\"')[0]
				subject = line.split('/resource/')[1].split('> <')[0]

				wf.write("sentence:" + sentence + '\n')

				for pattern in patterns:
					pattern = pattern.decode('utf-8')
					reg = re.compile(pattern)
					results = reg.finditer(sentence)

					if results:
						#for ppty in results:
						#	wf.write("relation:" + subject + '\t:\t' + ppty + '\n')
						for result in results:
							(b,e) = result.span()
							wf.write("relation:" + subject + '\t:\t' + sentence[b:e] + '\n')
		wf.close()


	def clean(self, filepath, threshold):
		'''
		function:
			given the human-labeled files and the threshold, return the entities that
			were correctly labeled more than threshold times, otherwise print the wrongly
			labeld entity information.
		parameters:
			filepath: path of human-labeled files
			threshold: the threshold
		''' 
		print("==========通过人工标注阈值去除实体==========")
		count = {}
		for file in filepath:
			with open(file, 'r') as f:
				for line in f.readlines():
					line = line.strip().decode('utf-8')
					if count.get(line, 0):
						count[line] += 1
					else:
						count[line] = 1

		removed_count = 0
		result = []
		for key,value in count.items():
			if value >= threshold:
				result.append(key)
			else:
				removed_count += 1
				#print key

		print("==========共去除"+str(removed_count)+"个实体==========")
		return result



	def clean_by_attr(self, clean_attr, entities, attr_file, filter_words):
		'''
		function:
			given entities and property files, entities with property containing
			filtered_words were wrongly labeled and print the error information, otherwise
			return the correctly labeled entities.
		parameters:
			clean_attr: property that used to clean the data, including ABSTRACT, CATEGORY,
			NAME, and SECTION
			entities: entities that will be cleaned
			attr_file: subject-attribute pair files
			filters: filtered_words
		'''
		print("==========通过" + clean_attr + "去除实体==========")
		removed_count = 0
		result = []
		if clean_attr == 'NAME':
			for entity in entities:
				remove = False
				for word in filter_words:
					if entity.find(word) != -1:
						remove = True

				if remove:
					#print entity
					removed_count += 1
				else:
					result.append(entity)


		else:
			result = entities

		f = open(attr_file,'r')
		for i,line in enumerate(f.readlines()):

			line = line.strip().decode('utf-8')
			subject = line.split(' <')[0]


			if subject in result:
				remove = False

				for word in filter_words:
					if line.find(word) != -1:
						remove = True
				if remove:
					#print subject
					result.remove(subject)
					removed_count += 1

		f.close()
		print("==========共去除" + str(removed_count) + "个实体==========")
		return result



if __name__ == "__main__":

	reload(sys)
	sys.setdefaultencoding('utf-8')

	assignment = Assignment()

	sentence = "万佛寺是中国成都一座已经不存在的佛教寺庙，遗址位于市一环路北二段与白马寺街交叉路口北侧，即成都老城西门外。"
	pattern_example = r"(位于)([^，|^。]+)"
	assignment.extract(sentence.decode('utf-8'), pattern_example.decode('utf-8'))

	#==========Assignment 1===========
	#==========提取位置信息============
	abstract_file = r'C:\Ariel\knowledge_graph\Assignment\Assignment\resource\Assignment1\abstracts.ttl'
	position_output = r'.\position_property.ttl'
	position_pattern = [r'(位于|坐落于)[^，|^。]+', r'(位在)[^，|^。|^的]+']
	assignment.extractFile(abstract_file, position_pattern, position_output)

	#==========提取始建时间============
	time_output = r'.\established_time_property.ttl'
	#time_pattern = [r'建于.*?年[^，|^。]+', r'[0-9]{0,4}年.*?建[^，|^。]+']
	time_pattern = [r'(建造于|始建于|初建于|建于)[^，|^。]+', r'(于|在).+(初|中叶|末|时代|年|年代)(创建|建成|修建)']
	assignment.extractFile(abstract_file, time_pattern, time_output)

	#=========提取别名信息=============
	alias_output = r'.\alias_property.ttl'
	alias_pattern = [r'(别|也|又|亦|俗|简|通|全|原|正式名)(称|名)[^，|^。]+',r'(称|名)(为|作)[^，|^。]+']
	assignment.extractFile(abstract_file, alias_pattern, alias_output)

	#========提取宗派信息==========
	section_output = r'.\section_property.ttl'
	section_pattern = [r'(属于|是|为)[^，|^。]+(派|宗)']
	assignment.extractFile(abstract_file, section_pattern, section_output)

	#==========Assignment 2===================
	#==========通过人工标注阈值去除实体==========
	threshold = 3
	filepath = []
	path = r'C:\Ariel\knowledge_graph\Assignment\Assignment\resource\Assignment2\entities_labeled'
	for i in range(1,5):
		filepath.append(path + '\\' + str(i) + '.txt')

	count_cleaned_entities = assignment.clean(filepath, threshold)
	count_cleaned_output = '.\\cleaned_entities_bythreshold.txt'
	with open(count_cleaned_output,'w') as f:
		f.write('\n'.join(count_cleaned_entities))


	#==========进一步通过属性值去除实体==========
	abstract_att = 'ABSTRACT'
	abstract_file = r'C:\Ariel\knowledge_graph\Assignment\Assignment\resource\Assignment2\abstracts.ttl'
	abstract_filters = ["官署","清真","阿訇","穆斯林","伊斯兰教","礼拜","天主教","出版"]
	abstract_cleaned_entities = assignment.clean_by_attr(abstract_att, count_cleaned_entities, abstract_file, abstract_filters)

	name_att = 'NAME'
	name_file = r'C:\Ariel\knowledge_graph\Assignment\Assignment\resource\Assignment2\aliases.ttl'
	name_filters = ["古墓","塑像","刘瑞","造像","建筑群"]
	name_cleaned_entities = assignment.clean_by_attr(name_att, abstract_cleaned_entities, name_file, name_filters)


	category_att = 'CATEGORY'
	category_file = r'C:\Ariel\knowledge_graph\Assignment\Assignment\resource\Assignment2\categories.ttl'
	category_filters = ["伊斯兰教", "天主教", "小说", "动画", "作品", "文库", "音乐", "影像", "人", "宫殿", "墓塔", "博物馆", "档案馆"]
	category_cleaned_entities = assignment.clean_by_attr(category_att, name_cleaned_entities, category_file, category_filters)


	section_att = 'SECTION'
	section_file = r'C:\Ariel\knowledge_graph\Assignment\Assignment\resource\Assignment2\sections.ttl'
	section_filters = ["木教派", "虎非耶教派", "哲合林耶教派"]
	section_cleaned_entities = assignment.clean_by_attr(section_att, category_cleaned_entities, section_file, section_filters)

	cleaned_output = ".\\cleaned_entities_byatts.txt"
	with open(cleaned_output, 'w') as f:
		f.write('\n'.join(section_cleaned_entities))