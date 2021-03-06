#!usr/bin/env python
from warnings import filterwarnings
import MySQLdb
import farmer_log
from common import *

filterwarnings("ignore", category = MySQLdb.Warning)

class Mysql_wrapper():

    def __init__(self, host, user, passwd, dataset):
        self.host       = host
        self.user       = user
        self.passwd     = passwd
        self.dataset    = dataset
        self.connection = \
            MySQLdb.Connect(host="%s" % (host,), user="%s" % (user,), passwd="%s" % (passwd,), db="%s" % (dataset,))

    def cursor(self):
        try:
            self.connection.ping()
        except Exception, e:
            self.connection = MySQLdb.Connect(self.host, self.user, self.passwd, self.dataset)
            farmer_log.info("The connection is too long, reconnect.")
        return self.connection.cursor()


    def __del__(self):
        self.connection.close()

    def init_database(self):
        """
        Perpare for MYSQL database and table
        Args:
            NULL

        Returns:
        """
        cursor = self.cursor()

        create_accounts_table_cmd = """CREATE TABLE IF NOT EXISTS accounts
        (id             INT             NOT NULL AUTO_INCREMENT,
         USER           VARCHAR(500)    NOT NULL,
         PASSWORD       VARCHAR(500)    NOT NULL,
         MAIL           VARCHAR(500)    NOT NULL,
         HAVE_LOGINED   BOOL            NOT NULL,
         PRIMARY KEY (id));"""

        create_docker_images_table_cmd  = """CREATE TABLE IF NOT EXISTS docker_images
        (id                   INT          NOT NULL AUTO_INCREMENT,
         REPOSITORY           VARCHAR(500) NOT NULL,
         TAG                  VARCHAR(500) NOT NULL,
         CUDA_VERSION         FLOAT        NOT NULL,
         CUDA_VERSION_STRING  VARCHAR(500) NOT NULL,
         CUDNN_VERSION        FLOAT        NOT NULL,
         CUDNN_VERSION_STRING VARCHAR(500) NOT NULL,
         TENSORFLOW           BOOL         NOT NULL,
         CAFFE                BOOL         NOT NULL,
         PRIMARY KEY (id));"""

        create_request_reports_table_cmd = """CREATE TABLE IF NOT EXISTS request_reports
        (id              INT          NOT NULL AUTO_INCREMENT,
         REQUEST_ID      VARCHAR(500) NOT NULL,
         DOCKER_ID       VARCHAR(500) NOT NULL,
         GPU_MODEL       VARCHAR(500) NOT NULL,
         MAIL_ADDRESS    VARCHAR(500) NOT NULL,
         FRAMEWORK       VARCHAR(500) NOT NULL,
         TOPOLOGY        VARCHAR(500) NOT NULL,
         BATCH_SIZE      VARCHAR(500) NOT NULL,
         ITERATION       VARCHAR(500) NOT NULL,
         REQUEST_TIME    DATETIME     NOT NULL DEFAULT NOW(),
         PRIMARY KEY (id));"""

        create_result_report_table_cmd = """CREATE TABLE IF NOT EXISTS result_reports
        (id            INT          NOT NULL  AUTO_INCREMENT,
        REQUEST_ID     VARCHAR(500) NOT NULL,
        DOCKER_ID      VARCHAR(500) NOT NULL,
        GPU_MODEL      VARCHAR(500) NOT NULL,
        FRAMEWORK      VARCHAR(500) NOT NULL,
        TOPOLOGY       VARCHAR(500) NOT NULL,
        BATCH_SIZE     INT          NOT NULL,
        SOURCE         VARCHAR(500) NOT NULL,
        ITERATION      INT          NOT NULL,
        SCORE          DOUBLE       NOT NULL,
        IMAGES_PRE_SEC DOUBLE       NOT NULL,
        PRIMARY KEY (id));"""

        #execute initalizing the user account table command
        self.create_table(create_accounts_table_cmd, cursor)

        # execute initalizing the docker_images command
        self.create_table(create_docker_images_table_cmd, cursor)

        # execute initalizing the request_reports command
        self.create_table(create_request_reports_table_cmd, cursor)

        # execute initalizing the result_reports command
        self.create_table(create_result_report_table_cmd, cursor)

        cursor.close()

    def create_account(self, user, password, mail):
        cursor = self.cursor()
        try:
            inserted_sql = '''INSERT INTO accounts
                  (USER,   PASSWORD,       MAIL, HAVE_LOGINED)
            VALUES("%s",   "%s",           "%s",    False);''' % \
                   (user,  password,       mail)
            farmer_log.debug(inserted_sql)
            cursor.execute(inserted_sql)
            self.connection.commit()
            output = cursor.fetchall()
            farmer_log.info(output)
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("inert_account_info:" + e.message)
        finally:
            cursor.close()

    def exists_mail(self, mail):
        result = False
        cursor = self.cursor()
        try:
            select_sql = """select id from accounts where
            MAIL = "%s";""" % mail
            farmer_log.info(select_sql)
            cursor.execute(select_sql)
            self.connection.commit()
            if 1 == cursor.rowcount:
                result = True
            elif 0 == cursor.rowcount:
                result = False
            else:
                farmer_log.error("The account have exists more than one.user[%s]" % user)
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("exists_account error [%s]" % e.message)
        return result

    def exists_user(self, user):
        result = False
        cursor = self.cursor()
        try:
            select_sql = """select id from accounts where
            USER = "%s";""" % user
            farmer_log.info(select_sql)
            cursor.execute(select_sql)
            self.connection.commit()
            if 1 == cursor.rowcount:
                result = True
            elif 0 == cursor.rowcount:
                result = False
            else:
                farmer_log.error("The account have exists more than one.user[%s]" % user)
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("exists_account error [%s]" % e.message)
        return result

    def account_login(self, mail, password):
        result = (-1, "")
        cursor = self.cursor()
        try:
            login_sql = """select id, MAIL from accounts
            where MAIL = "%s" AND PASSWORD = "%s";""" % (mail, password)
            farmer_log.info(login_sql)
            rowcount = cursor.execute(login_sql)
            self.connection.commit()
            if rowcount == 1:
                output = cursor.fetchone()
                result = (int(output[0]), str(output[1]))
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("account_login error [%s]" % e.message)
        return result
        
    def account_logout(self, mail, password):
        cursor = self.cursor()
        try:
            login_sql = """UPDATE accounts
            SET HAVE_LOGINED = 0
            where MAIL = "%s" AND PASSWORD = "%s";""" % (mail, password)
            farmer_log.info(login_sql)
            cursor.execute(login_sql)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("account_logout error [%s]" % e.message)

    def create_table(self, sql_command, cursor):
        farmer_log.info("init table : [%s]" % sql_command)
        cursor.execute(sql_command)
        farmer_log.info(cursor.fetchall())
        self.connection.commit()

    def has_image_in_db_by_rep_tag(self, repository, tag):
        result = False
        cursor = self.cursor()
        try:
            seach_image = "SELECT repository, tag FROM docker_images WHERE REPOSITORY = '%s' AND TAG = '%s';" % (repository, tag)
            farmer_log.debug(seach_image)
            cursor.execute(seach_image)
            farmer_log.debug(cursor.rowcount)
            if (-1 != cursor.rowcount) and (0 != cursor.rowcount):
                result = True
            output = cursor.fetchall()
            farmer_log.info(output)
        except Exception as e:
            farmer_log.error("has_image_in_db_by_rep_tag:" + e.message)
            self.connection.rollback()
        finally:
            cursor.close()
        return result

    def inert_item_in_docker_images_table(self, repository, tag, cuda_version, cuda_version_str, cudnn_version, cudnn_version_str, have_tensorflow, have_caffe):
        cursor = self.cursor()
        try:
            inserted_sql = 'INSERT INTO docker_images (REPOSITORY, TAG,\
             CUDA_VERSION, CUDA_VERSION_STRING, CUDNN_VERSION,\
             CUDNN_VERSION_STRING, TENSORFLOW, CAFFE) \
             VALUES("%s", "%s", %f, "%s", %f, "%s", %d, %d);' % \
              (repository, tag, cuda_version, cuda_version_str, cudnn_version,\
               cudnn_version_str, have_tensorflow, have_caffe)
            farmer_log.debug(inserted_sql)
            cursor.execute(inserted_sql)
            self.connection.commit()
            output = cursor.fetchall()
            farmer_log.info(output)
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("inert_item_in_docker_images_table:" + e.message)
        finally:
            cursor.close()

    def inert_item_in_request_reports(self, resquest_id, docker_id, gpu_model, \
                                      mail_addr, framework, topology, \
                                      batch_size, iteration):
        cursor = self.cursor()
        try:
            inserted_sql = 'INSERT INTO request_reports\
            (REQUEST_ID,   DOCKER_ID,  GPU_MODEL,  MAIL_ADDRESS,  FRAMEWORK,  TOPOLOGY,  BATCH_SIZE,   ITERATION) \
      VALUES("%s",         "%s",       "%s",       "%s",          "%s",       "%s",      "%s",         "%s");' % \
            (resquest_id,  docker_id,  gpu_model,  mail_addr,     framework,  topology,  batch_size,   iteration)
            farmer_log.debug(inserted_sql)
            cursor.execute(inserted_sql)
            self.connection.commit()
            output = cursor.fetchall()
            farmer_log.info(output)
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("inert_item_in_request_reports:" + e.message)
        finally:
            cursor.close()

    def inert_item_in_result_reports(self, resquest_id, docker_id, gpu_model, \
                                     framework, topology, batch_size, source, \
                                     iteration, score, images_pre_sec):
        cursor = self.cursor()
        try:
            inserted_sql = 'INSERT INTO result_reports\
            (REQUEST_ID,   DOCKER_ID,  GPU_MODEL,  FRAMEWORK,  TOPOLOGY,  BATCH_SIZE,  SOURCE,   ITERATION,  SCORE,    IMAGES_PRE_SEC) \
      VALUES("%s",         "%s",       "%s",       "%s",       "%s",      %d,          "%s",     %d,         %f,       %f);' % \
            (resquest_id,  docker_id,  gpu_model,  framework,  topology,  batch_size,  source,   iteration,  score,    images_pre_sec)
            cursor.execute(inserted_sql)
            self.connection.commit()
            output = cursor.fetchall()
            farmer_log.info(output)
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("inert_item_in_result_report:" + e.message)
        finally:
            cursor.close()

    def get_request_reports(self, start_index, count):
        header = ["REQUEST_ID", "DOCKER_ID", "GPU_MODEL", "MAIL_ADDRESS", "FRAMEWORK", "TOPOLOGY", "BATCH_SIZE", "ITERATION", "REQUEST_TIME"]
        result = DataMediator(header)
        cursor = self.cursor()
        try:
            seach_image = "SELECT %s FROM request_reports order by REQUEST_TIME desc limit %d, %d;" % (", ".join(header), start_index, count)
            farmer_log.debug(seach_image)
            cursor.execute(seach_image)
            self.connection.commit()
            rowcount = cursor.rowcount
            farmer_log.debug("The result row count is %d" % rowcount)
            for i in range(rowcount):
                output = cursor.fetchone()
                result.append((output[0], \
                               output[1], \
                               output[2], \
                               output[3], \
                               output[4], \
                               output[5], \
                               output[6], \
                               output[7], \
                               output[8]))
                farmer_log.info(output)
        except Exception as e:
            farmer_log.error("get_request_reports:" + e.message)
            self.connection.rollback()
        finally:
            cursor.close()
        return result

    def get_result_by_request_id(self, request_id):
        header = ("REQUEST_ID", "DOCKER_ID", "GPU_MODEL", "FRAMEWORK", "TOPOLOGY", "BATCH_SIZE", "SOURCE", "ITERATION", "SCORE", "IMAGES_PRE_SEC", "MAIL_ADDRESS")
        result = DataMediator(header)
        cursor = self.cursor()
        email = ""
        try:
            search_email = "SELECT MAIL_ADDRESS FROM request_reports WHERE REQUEST_ID = '%s';" % (request_id)
            cursor.execute(search_email)
            self.connection.commit()
            if cursor.rowcount == 1:
                email = cursor.fetchone()
            else:

                farmer_log.error("The request email have wrong number. The rowcount[%d]" % cursor.rowcount)
                farmer_log.error(cursor.fetchall())

            search_image = "SELECT \
            REQUEST_ID,\
            DOCKER_ID,\
            GPU_MODEL,\
            FRAMEWORK,\
            TOPOLOGY,\
            BATCH_SIZE,\
            SOURCE,\
            ITERATION,\
            SCORE,\
            IMAGES_PRE_SEC FROM result_reports WHERE REQUEST_ID = '%s';" % request_id
            farmer_log.debug(search_image)
            cursor.execute(search_image)
            self.connection.commit()

            rowcount = cursor.rowcount
            farmer_log.debug("The result row count is %d" % rowcount)
            for i in range(rowcount):
                output = cursor.fetchone()
                farmer_log.info(output)
                result.append((output[0], \
                              output[1], \
                              output[2], \
                              output[3], \
                              output[4], \
                              output[5], \
                              output[6], \
                              output[7], \
                              "%.2f" % output[8], \
                              "%.2f" % output[9], \
                              email))
                farmer_log.info(output)
        except Exception as e:
            farmer_log.error("get_result_by_request_id:" + e.message)
            self.connection.rollback()
        finally:
            cursor.close()
        return result

    def has_image_in_db_by_cuda_cuddn(self, cuda_string, cuddn_string):
        result = False
        cursor = self.cursor()
        try:
            seach_image = "SELECT repository, tag FROM docker_images WHERE CUDA_VERSION_STRING = '%s' AND CUDNN_VERSION_STRING = '%s';" % (cuda_string, cuddn_string)
            farmer_log.debug(seach_image)
            cursor.execute(seach_image)
            farmer_log.debug(cursor.rowcount)
            if (-1 != cursor.rowcount) and (0 != cursor.rowcount):
                result = True
            output = cursor.fetchall()
            farmer_log.info(output)
        except Exception as e:
            self.connection.rollback()
            farmer_log.error("has_image_in_db_by_cuda_cuddn" + e.message)
        finally:
            cursor.close()
        return result

    def get_detailed_info_from_db(self, repository, tag):
        row = None
        cursor = self.cursor()
        try:
            select_sql = "SELECT * FROM docker_images WHERE REPOSITORY = '%s' AND TAG = '%s';" % (repository, tag)
            farmer_log.info(select_sql)
            cursor.execute(select_sql)
            numrows = int(cursor.rowcount)
            if numrows == 1:
                row = cursor.fetchone()
            else:
                farmer_log.error("the result numrows[%d] which is not 1." % numrows)
            output = cursor.fetchall()
            farmer_log.info(output)
        except Exception as e:
            farmer_log.error("get_detailed_info_from_db" + e.message)
        finally:
            cursor.close()
        return row



if __name__ == "__main__":
    wrapper = Mysql_wrapper("localhost", "root", "RACQ4F6c")
    wrapper.init_database()
    wrapper.inert_item_in_docker_images_table("nvidia/cuda", "7.5-cudnn5.1rc-devel-ubuntu14.04-caffe-pcs", 7.5,\
                                            "cuda_7.5.18", 5.0, "cudnn-7.5-linux-x64-v5.0-rc", False, True)
   # wrapper.inert_item_in_result_reports(1, 1, "GPU_MODULE", "a@c.com", "framework", "topology", 0, 100)
    print wrapper.get_detailed_info_from_db("nvidia/cuda", "7.5-cudnn5.1rc-devel-ubuntu14.04-caffe-pcs")
    #print wrapper.has_image_in_db_by_cuda_cuddn("cuda_7.5.18", "cudnn-7.5-linux-x64-v5.0-rc")

    ##print wrapper.has_image_in_db_by_cuda_cuddn("cuda_7.5.18", "cudnn-7.5-linux-x64-v5.0-rc")
