# encoding: utf-8
# Created on 2014-5-28
# @author: binge
from utils.conns_helper import mongo_exec, MongoHelper
from utils import settings

class SectionService():

    def gene_sections_page(self, curr_page, book_sections_size, sections_curror):
        sections_page = {'curr_page' : curr_page}
        sections = []
        i = 0
        for section in sections_curror:
            sections.append(section)
            i += 1
            if i >= book_sections_size:
                sections_page['next_page'] = curr_page + 1
                break
        sections = sections[:book_sections_size]
        sections_page['sections'] = sections

        if curr_page > 1:
            sections_page['prev_page'] = curr_page - 1
        return sections_page


    @mongo_exec(mongo=MongoHelper.get_mongo())
    def find_sections_page_by_id_site(self, b_id, site, curr_page=None, mongo=None):
        if not curr_page or int(curr_page) < 1:
            curr_page = 1
        else:
            curr_page = int(curr_page)
        conditions = {'b_id' : b_id}
        if site:
            conditions['source_short_name'] = site
        sections_cursor = mongo.bookshelf.sections.find(conditions).sort([('crawl_time', -1)]).skip((curr_page - 1) * settings.book_sections_size).limit(settings.book_sections_size * 2)
        return self.gene_sections_page(curr_page, settings.book_sections_size, sections_cursor)
