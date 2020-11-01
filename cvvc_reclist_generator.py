from collections import namedtuple
from random import choice, shuffle


CVV = namedtuple("CVV", "cvv c cv vr c_vel v_vel",
                 defaults=("R", "R", "R", "R", 0, 0))


class ReclistGenerator:
    CVV_list = []
    cvv_set = set()
    c_set = set()
    cv_set = set()
    vr_set = set()
    vc_set = set()
    c_idx_dict = {}
    cv_idx_dict = {}
    vr_idx_dict = {}
    reclist = []
    oto = []

    def read_dict(self, dict_path: str):
        with open(dict_path, mode="r") as f:
            cvvc_dict = f.read()

        for i, line in enumerate(cvvc_dict.splitlines()):
            if line == "":
                break
            line = line.strip()
            para_list = line.split(",")
            for j, para in enumerate(para_list):
                try:
                    para_list[j] = int(para)
                except ValueError:
                    pass
            self.CVV_list.append(CVV(*para_list))
            self.cvv_set.add(para_list[0])
            self.c_set.add(para_list[1])
            self.cv_set.add(para_list[2])
            self.vr_set.add(para_list[3])
            self.c_idx_dict.setdefault(para_list[1], []).append(i)
            self.cv_idx_dict.setdefault(para_list[2], []).append(i)
            self.vr_idx_dict.setdefault(para_list[3], []).append(i)

        for vr in self.vr_set:
            for c in self.c_set:
                self.vc_set.add((vr, c))

    def find_cvv(self, cvv: str = None, c: str = None,
                 cv: str = None, vr: str = None, exception: set=None) -> CVV or None:
        '''输入cvv，c，cv，vr来查找整音，并返回类CVV（找不到则返回None）

        :param cvv: 整音，如“bai”，“cai”等整字拼音，只能够单独使用。
        :param c: 辅音，如”b“，”c“等辅音拼音，可以和参数vr一同使用，
                单独使用时随机选择含有该辅音的整音。
        :param cv: 半音，整音去除韵尾的部分，如”bai“对应”ba“，可以和参数c一同使用，
        :param vr: 韵尾，如“ai”，“ong”等韵尾拼音，可以和参数c一同使用。
        :param exception: 给定一个集合，则返回的整音不会包含列表内含有的元素。
                当前只能与参数c一同使用，且给定的为vr集合（我懒得补完了Ok？
        :return: 如果找到了则返回类CVV，否则返回None。
        '''
        if cvv:
            for e_cvv in self.CVV_list:
                if e_cvv.cvv == cvv:
                    return e_cvv

        elif c is not None and vr is not None:
            for vr_idx in self.vr_idx_dict[vr]:
                cvv = self.CVV_list[vr_idx]
                if cvv.c == c:
                    return cvv

        elif cv is not None and vr is not None:
            for vr_idx in self.vr_idx_dict[vr]:
                cvv = self.CVV_list[vr_idx]
                if cvv.cv == cv:
                    return cvv

        elif c is not None:
            if exception:
                c_idx_list = self.c_idx_dict[c]
                shuffle(c_idx_list)
                for c_idx in c_idx_list:
                    cvv = self.CVV_list[c_idx]
                    if cvv.vr not in exception:
                       return cvv
            else:
                c_idx = choice(self.c_idx_dict[c])
                return self.CVV_list[c_idx]

        elif cv is not None:
            cv_idx = choice(self.cv_idx_dict[cv])
            return self.CVV_list[cv_idx]

        elif vr is not None:
            vr_idx = choice(self.vr_idx_dict[vr])
            e_cvv = self.CVV_list[vr_idx]
            return e_cvv

    def gen_cvvc_reclist(self, length: int = 6, group=False, cv_head=True,
                         plan_b=False, random=True, merge_cv=False, gottal: set=None):
        '''用于生成cvvc录音表

        :param length: 每一行的字数。
        :param group: 该录音方式会以每两个音（A，B）为一组来组成行，
                根据其包含未收录vc的情况会以一下方式排列：AABBA，ABBA，ABA，
                其余未收录的vc会以不规则（即乱序）的方式进行收录，每行字数为length。
        :param cv_head: 是否收录所有的开头音。
        :param plan_b: 沿用Hr.J式CVVC录音表的录音方式，每个整音会重复三次成一行
                即 aa_aa_aa 请使用5到8字BGM并将最后一字读满，同时oto会生成长音素aa L
        :param random: 是否以乱序的方式收录余下的vc部（否的话相对好读但每字oto数会降低。
        :param merge_cv: 是否合并cv部，如”ba“和”bai“合并为”ba“。
        :param gottal: 对于粤语等含有入声的语言，因为入声表现为强烈的停顿，因此可以不进行vc部的收录。
                当不需要入声vc时，需要输入一个包含入声vr的set，如{"aap"}。
        :return: 生成的录音表会收录在self.reclist当中。
        '''
        vc_set, vr_set = self.vc_set.copy(), self.vr_set.copy()
        cv_set, cv_head_set = self.cv_set.copy(), self.cv_set.copy()
        cvv_set, cvv_head_set = self.cvv_set.copy(), self.cvv_set.copy()

        # 如果不需要入声vc部
        if gottal is not None:
            gottal_vc_set = set()
            for gottal_vr in gottal:
                for c in self.c_set:
                    # 找到所有的入声vc部
                    gottal_vc_set.add((gottal_vr, c))
            # 将其从总vc中去除
            vc_set -= gottal_vc_set

        if plan_b:
            for cvv in self.CVV_list:
                self.reclist.append([cvv]*3)
                vc_set -= {(cvv.vr, cvv.c)}
                if merge_cv:
                    cv_set -= {cvv.cv}
                    if cv_head:
                        cv_head_set -= {cvv.cv}
                else:
                    cvv_set -= {cvv.cvv}
                    if cv_head:
                        cvv_head_set -= {cvv.cvv}
                vr_set -= {cvv.vr}

        # 是否以非分组的方式编写录音表
        if not group and not plan_b:
            i = 0
            row = []
            #遍历所有的整音进行排列
            for cvv in self.CVV_list:
                # 行内延伸
                if i < length:
                    row.append(cvv)
                    # 尝试收录vc（当i为0即开头时会发生错误，此时则跳过
                    try:
                        vc_set -= {(row[i].vr, row[i+1].c)}
                    except IndexError:
                        pass
                    # 根据是否合并cv部分情况收录cv
                    if i > 0:
                        if merge_cv:
                            cv_set -= {cvv.cv}
                        else:
                            cvv_set -= {cvv.cvv}
                    i += 1

                # 到达行内指定字数时
                elif i == length:
                    # 根据是否合并cv分情况收录开头音
                    if cv_head:
                        if merge_cv:
                            cv_head_set -= {row[0].cv}
                        else:
                            cvv_head_set -= {row[0].cvv}
                    # 收录韵尾
                    vr_set -= {row[-1].vr}
                    # 将该行添加到self.reclist当中
                    self.reclist.append(row)
                    row = []
                    i = 0

            # 添加末尾字数未到length的可能遗漏的行
            if row and row != self.reclist[-1]:
                self.reclist.append(row)
                if cv_head and merge_cv:
                    cv_head_set -= {row[0].cv}
                elif cv_head and not merge_cv:
                    cvv_head_set -= {row[0].cvv}
                vr_set -= {row[-1].vr}

        elif group:
            # AABBA part
            for cvv1 in self.CVV_list:
                for cvv2 in self.CVV_list:
                    # 筛选条件一
                    if cvv1.c == cvv2.c or cvv1.vr == cvv2.vr:
                        break
                    vcs = {(cvv1.vr, cvv1.c), (cvv1.vr, cvv2.c),
                           (cvv2.vr, cvv1.c), (cvv2.vr, cvv2.c)}
                    if vcs <= vc_set:
                        row = [cvv1, cvv1, cvv2, cvv2, cvv1]
                        self.reclist.append(row)
                        vc_set -= vcs
                        if merge_cv:
                            cv_set -= {cvv1.cv, cvv2.cv}
                            if cv_head:
                                cv_head_set -= {cvv1.cv}
                        else:
                            cvv_set -= {cvv1.cvv, cvv2.cvv}
                            if cv_head:
                                cvv_head_set -= {cvv1.cvv}
                        vr_set -= {cvv1.vr}

            # ABBA
            for cvv1 in self.CVV_list:
                for cvv2 in self.CVV_list:
                    # 筛选条件一
                    if cvv1.c == cvv2.c or cvv1.vr == cvv2.vr:
                        break
                    vcs = {(cvv1.vr, cvv1.c), (cvv1.vr, cvv2.c),
                           (cvv2.vr, cvv1.c), (cvv2.vr, cvv2.c)}
                    if len(vcs & vc_set) == 3:
                        if (cvv1.vr, cvv1.c) in vc_set:
                            row = [cvv2, cvv1, cvv1, cvv2]
                        else:
                            row = [cvv1, cvv2, cvv2, cvv1]
                        self.reclist.append(row)
                        vc_set -= vcs
                        if merge_cv:
                            cv_set -= {cvv1.cv, cvv2.cv}
                            if cv_head:
                                cv_head_set -= {row[0].cv}
                        else:
                            cvv_set -= {cvv1.cvv, cvv2.cvv}
                            if cv_head:
                                cvv_head_set -= {row[0].cvv}
                        vr_set -= {row[-1].vr}

            # ABA
            ABA_cvv_group = set()
            for cvv1 in self.CVV_list:
                for cvv2 in self.CVV_list:
                    if cvv1.c == cvv2.c or cvv1.vr == cvv2.vr:
                        break
                    vcs = {(cvv1.vr, cvv1.c), (cvv1.vr, cvv2.c),
                           (cvv2.vr, cvv1.c), (cvv2.vr, cvv2.c)}
                    if len(vcs & vc_set) == 2:
                        ABA_cvv_group.add((cvv1, cvv2))
                        vc_set -= {(cvv1.vr, cvv2.c), (cvv2.vr, cvv1.c)}
                        if merge_cv:
                            cv_set -= {cvv1.cv, cvv2.cv}
                        else:
                            cvv_set -= {cvv1.cvv, cvv2.cvv}

            # ABACDC
            while ABA_cvv_group:
                cvv_group1 = ABA_cvv_group.pop()
                cvv1, cvv2 = cvv_group1[0], cvv_group1[1]
                try:
                    cvv_group2 = ABA_cvv_group.pop()
                    cvv3, cvv4 = cvv_group2[0], cvv_group2[1]
                    if (cvv1.vr, cvv3.c) in vc_set:
                        row = [cvv1, cvv2, cvv1, cvv3, cvv4, cvv3]
                    elif(cvv1.vr, cvv4.c) in vc_set:
                        row = [cvv1, cvv2, cvv1, cvv4, cvv3, cvv4]
                    elif (cvv2.vr, cvv3.c) in vc_set:
                        row = [cvv2, cvv1, cvv2, cvv3, cvv4, cvv3]
                    else:
                        row = [cvv2, cvv1, cvv2, cvv4, cvv3, cvv4]
                    if cv_head and merge_cv:
                        cv_head_set -= {row[0].cv}
                    elif cv_head and not merge_cv:
                        cvv_head_set -= {row[0].cvv}
                    vc_set -= {(row[2].vr, row[3].c)}

                except KeyError:
                    if merge_cv:
                        if cvv1.cv in cv_head_set:
                            row = [cvv1, cvv2, cvv1]
                        else:
                            row = [cvv2, cvv1, cvv2]
                        if cv_head:
                            cv_head_set -= {row[0].cv}
                    else:
                        if cvv1.cvv in cvv_head_set:
                            row = [cvv1, cvv2, cvv1]
                        else:
                            row = [cvv2, cvv1, cvv2]
                        if cv_head:
                            cvv_head_set -= {row[0].cvv}
                self.reclist.append(row)
                vr_set -= {row[-1].vr}

        # 是否以乱序方式收录余下的vc部
        if random:
            # 乱序方式收录
            i = 0
            row = []
            while vc_set:
                # 行开头时，从未收录的vc_set取出一个vc部
                if i == 0:
                    vc = vc_set.pop()
                    cvv1 = self.find_cvv(vr=vc[0])
                    cvv2 = self.find_cvv(c=vc[1], exception=gottal)
                    row.extend([cvv1, cvv2])
                    # 依情况收录cv部
                    if merge_cv:
                        cv_set -= {cvv2.cv}
                    else:
                        cvv_set -= {cvv2.cvv}
                    i += 2

                # 行内延伸
                elif i < length:
                    vr = row[-1].vr
                    # 遍历含有该vr可能用于接续的整音
                    for vr_idx in self.vr_idx_dict[vr]:
                        cvv = self.CVV_list[vr_idx]
                        # 不收录入声vc时跳过含有入声的整音
                        if gottal and cvv.vr in gottal:
                            break
                        if (vc := (vr, cvv.c)) in vc_set:
                            row.append(cvv)
                            vc_set.remove(vc)
                            # 按情况收录cv部
                            if merge_cv:
                                cv_set -= {cvv.cv}
                            else:
                                cvv_set -= {cvv.cvv}
                            i += 1
                            break
                    # 包含前一个音vr的vc部已经全部收录完毕
                    else:
                        # 如果剩余空位大于两个
                        if i < length - 1:
                            vc = vc_set.pop()
                            cvv1 = self.find_cvv(vr=vc[0])
                            cvv2 = self.find_cvv(c=vc[1], exception=gottal)
                            row.extend([cvv1, cvv2])
                            if merge_cv:
                                cv_set -= {cvv1.cv, cvv2.cv}
                            else:
                                cvv_set -= {cvv1.cvv, cvv2.cvv}
                            i += 2
                        # 若只剩一个空位 则计数i直接跳满到下一行
                        else:
                            i = length

                # 行内收录完毕
                elif i == length:
                    cvv1 = row[0]
                    cvv2 = row[-1]
                    # 依情况收录开头音
                    if cv_head and merge_cv:
                        if cvv1.cv in cv_head_set:
                            cv_head_set.remove(cvv1.cv)
                        # 如果该开头音已经被收录，尝试寻找具有相同vr的未收录cv的整音
                        else:
                            if cv_head_set:
                                for cv in cv_head_set:
                                    if cvv := self.find_cvv(cv=cv, vr=cvv1.vr):
                                        row[0] = cvv
                                        cv_head_set.remove(cvv.cv)
                                        break
                    elif cv_head and not merge_cv:
                        cvv_head_set -= {cvv1.cvv}
                    # 收录韵尾
                    vr_set -= {cvv2.vr}
                    # 收录row并初始化
                    self.reclist.append(row)
                    row = []
                    i = 0

        # 以非乱序形式收录余下vc部
        else:
            # 创建一个list记录vc整音组
            re_vc_set_list = []
            # 按照c的顺序依次给每个未收录的vc部寻找整音组
            for c in self.c_set:
                c_cvv = self.find_cvv(c=c)
                for vc in vc_set:
                    if vc[1] == c:
                        vr_cvv = self.find_cvv(vr=vc[0])
                        re_vc_set_list.append((vr_cvv, c_cvv))

            # 将vc整音组收入reclist中
            i = 0
            row = []
            for re_vc in re_vc_set_list:
                if i < length - 1:
                    row.extend([re_vc[0], re_vc[1]])
                    if i == 0:
                        if merge_cv:
                            cv_set -= {re_vc[1].cv}
                        else:
                            cvv_set -= {re_vc[1].cvv}
                    else:
                        if merge_cv:
                            cv_set -= {re_vc[0].cv, re_vc[1].cv}
                        else:
                            cvv_set -= {re_vc[0].cvv, re_vc[1].cvv}
                    i += 2
                else:
                    if cv_head and merge_cv:
                        if cv_head_set:
                            if row[0].cv not in cv_head_set:
                                vr = row[0].vr
                                for cv in cv_head_set:
                                    cvv = self.find_cvv(cv=cv, vr=vr)
                                    if cvv:
                                        row[0] = cvv
                                        cv_head_set -= {cvv.cv}
                                        break
                    elif cv_head and not merge_cv:
                        if cvv_head_set:
                            if row[0].cvv not in cvv_head_set:
                                vr = row[0].vr
                                for cv in cvv_head_set:
                                    cvv = self.find_cvv(cvv=cv)
                                    if cvv.vr == vr:
                                        row[0] = cvv
                                        cvv_head_set -= {cvv.cvv}
                                        break
                    vr_set -= {row[-1].vr}
                    self.reclist.append(row)
                    row = [re_vc[0], re_vc[1]]
                    i = 2

        # 收录可能遗漏的行
        if row and row != self.reclist[-1]:
            self.reclist.append(row)
            if cv_head and merge_cv:
                cv_head_set -= {row[0].cv}
            elif cv_head and not merge_cv:
                cvv_head_set -= {row[0].cvv}
            vr_set -= {row[-1].vr}

        # 收录余下的cv_head（如果要求的话
        i = 0
        row = []
        if cv_head and merge_cv:
            for cv in cv_head_set:
                r = CVV()
                cvv = self.find_cvv(cv=cv)
                cv_set -= {cvv.cv}
                vr_set -= {cvv.vr}
                if i < length - 1:
                    row.extend([cvv, r])
                    i += 2
                else:
                    self.reclist.append(row)
                    row = [cvv, r]
                    i = 2

        elif cv_head and not merge_cv:
            for cv in cvv_head_set:
                r = CVV()
                cvv = self.find_cvv(cvv=cv)
                cvv_set -= {cvv.cvv}
                vr_set -= {cvv.vr}
                if i < length - 1:
                    row.extend([cvv, r])
                    i += 2
                else:
                    self.reclist.append(row)
                    row = [cvv, r]
                    i = 2

        if row and row != self.reclist[-1]:
            self.reclist.append(row)
            if cv_head and merge_cv:
                cv_head_set -= {row[0].cv}
            elif cv_head and not merge_cv:
                cvv_head_set -= {row[0].cvv}
            vr_set -= {row[-1].vr}

        # 收录余下cv部
        i = 0
        row = []
        if merge_cv:
            for cv in cv_set:
                if i < length:
                    if i == 0:
                        row.extend([self.find_cvv(cv=cv)]*2)
                        i = 2
                    else:
                        row.append(self.find_cvv(cv=cv))
                        i += 1
                else:
                    self.reclist.append(row)
                    vr_set -= {row[-1].vr}
                    row = [self.find_cvv(cv=cv)]
                    i = 1
        else:
            for cv in cvv_set:
                if i < length:
                    if i == 0:
                        row.extend([self.find_cvv(cvv=cv)]*2)
                        i = 2
                    else:
                        row.append(self.find_cvv(cvv=cv))
                        i += 1
                else:
                    self.reclist.append(row)
                    vr_set -= {row[-1].vr}
                    row = [self.find_cvv(cvv=cv)]
                    i = 1

        if row and row != self.reclist[-1]:
            self.reclist.append(row)
            vr_set -= {row[-1].vr}

        # 收录余下的vr
        i = 0
        row = []
        for vr in vr_set:
            r = CVV()
            cvv = self.find_cvv(vr=vr)
            if i < length - 1:
                row.extend([cvv, r])
                i += 2
            else:
                self.reclist.append(row)
                row = [cvv, r]
                i = 2

        if row and row != self.reclist[-1]:
            self.reclist.append(row)

    def print_reclist(self):
        '''用print打印当前录音表

        :return: None
        '''
        for row in self.reclist:
            for cvv in row:
                print("_%s" % cvv.cvv, end="")
            print()

    def gen_oto(self, cv_head=True, merge_cv=False, gottal=None, debug=True,
                plan_b=False, max_vc: int=1, max_cv: int=1, max_vr: int=1,
                bpm: float=120, length: int=6):
        '''用于生成cvvc oto

        :param cv_head: 是否生成开头音
        :param merge_cv: 是否合并cv部
        :param gottal: 是否生成gottal vc
        :param debug: 检查是否遗漏oto（仅当oto份数为1时有明确性
        :param plan_b: 是否将每个整音重复三次形成一行的录音方案
        :param max_vc: 最大的相同vc oto数
        :param max_cv: 最大的相同cv oto数，包含开头音（如果要求
        :param max_vr: 最大的相同vr oto数
        :param bpm: 录音用的bpm
        :param length: 录音表的最大行字数
        :return: 生成的oto会依次按照vc、cv、vr的方式收录到self.oto中
        '''

        # 为了方便将入声设为空集
        if gottal is None:
            gottal = set()

        # 用于分组存放oto
        vc_part = []
        cv_part = []
        cv_head_part = []
        vr_part = []

        # 用于记录每个oto出现的次数
        vc_dict = {}
        cv_dict = {}
        cv_head_dict = {}
        vr_dict = {}

        # 历遍每行的每个整音，i用于判断是否生成长音oto
        for i, row in enumerate(self.reclist):
            # 生成该行的wav字符串
            wav = ""
            for cvv in row:
                wav += "_%s" % cvv.cvv
            wav += ".wav="
            # j用于判断前后音符是否为空，再以此判断是否生成开头音和结尾音
            for j, cvv in enumerate(row):
                # 当前音符为R时跳过
                if cvv.cvv == "R":
                    continue

                # 生成各部分oto的数值
                bpm_para = float(bpm / 120)
                rhy = bpm_para*(1200 + j*500)  # 每一拍的位置
                ovl = bpm_para*80  # 重叠线
                c_vel = bpm_para*cvv.c_vel  # 该音符的辅音长度
                if j > 0:
                    v_vel = bpm_para*row[j-1].v_vel  # 上一个音的韵尾长度
                else:
                    v_vel = 100

                # vc
                if j > 0:
                    vr = row[j-1].vr
                    c = cvv.c
                    if vr == "R" or c == "R":
                        pass
                    elif vr in gottal:
                        pass
                    else:
                        if (vr, c) in vc_dict:
                            vc_dict[(vr, c)] += 1
                        else:
                            vc_dict[(vr, c)] = 1
                        if (n := vc_dict[(vr, c)]) <= max_vc:
                            ofs = rhy - c_vel - v_vel - ovl  #左线
                            pre = ovl + v_vel  # 红线
                            con = pre + c_vel / 6  # 非拉伸的紫线
                            cuf = - (con + c_vel / 6)  # 右线
                            numl_para = ",{:.1f},{:.1f},{:.1f},{:.1f}" \
                                    ",{:.1f}".format(ofs, con, cuf, pre, ovl)
                            if n == 1:
                                vc = "%s %s" % (vr, c)
                            else:
                                vc = "%s %s%s" % (vr, c, n)
                            vc_part.append(wav + vc + numl_para)

                # cv
                if j > 0:
                    if merge_cv:
                        cv = cvv.cv
                    else:
                        cv = cvv.cvv
                    if cv in cv_dict:
                        cv_dict[cv] += 1
                    else:
                        cv_dict[cv] = 1
                    if (n := cv_dict[cv]) <= max_cv:
                        ofs = rhy - c_vel
                        ovl = c_vel / 3
                        pre = c_vel
                        con = pre + bpm_para*100
                        cuf = - (pre + bpm_para*(500 - 100 - cvv.v_vel - row[j+1].c_vel))
                        numl_para = ",{:.1f},{:.1f},{:.1f},{:.1f}" \
                                    ",{:.1f}".format(ofs, con, cuf, pre, ovl)
                        if n > 1:
                            cv += str(n)
                        cv_part.append(wav + cv + numl_para)

                # cv_L
                if plan_b and i < len(self.CVV_list) and j == 2:
                    ofs = rhy - c_vel
                    ovl = c_vel / 3
                    pre = c_vel
                    con = pre + bpm_para*100
                    cuf = -(pre + bpm_para*(500*(length-j) - cvv.v_vel))
                    numl_para = ",{:.1f},{:.1f},{:.1f},{:.1f}" \
                                ",{:.1f}".format(ofs, con, cuf, pre, ovl)
                    if merge_cv:
                        cv_L = cvv.cv + "_L"
                    else:
                        cv_L = cvv.cvv + "_L"
                    cv_part.append(wav + cv_L + numl_para)

                # cv head
                if cv_head:
                    if merge_cv:
                        _cv = cvv.cv
                    else:
                        _cv = cvv.cvv
                    if j == 0 or row[j-1].cvv == "R":
                        if _cv in cv_head_dict:
                            cv_head_dict[_cv] += 1
                        else:
                            cv_head_dict[_cv] = 1
                        if (n := cv_head_dict[_cv]) <= max_cv:
                            ofs = rhy - c_vel
                            ovl = 30
                            pre = c_vel
                            con = pre + bpm_para*100
                            cuf = - (pre + bpm_para*(500 - 100 - cvv.v_vel - row[j+1].c_vel))
                            numl_para = ",{:.1f},{:.1f},{:.1f},{:.1f}" \
                                        ",{:.1f}".format(ofs, con, cuf, pre, ovl)
                            if n > 1:
                                cv = "- %s%s" % (_cv, n)
                            else:
                                cv = "- %s" % _cv
                            cv_head_part.append(wav + cv + numl_para)

                # vr
                if j == len(row)-1 or (j < len(row)-1 and row[j+1].cvv == "R"):
                    vr = cvv.vr
                    if vr in vr_dict:
                        vr_dict[vr] += 1
                    else:
                        vr_dict[vr] = 1
                    if (n := vr_dict[vr]) <= max_vr:
                        ovl = bpm_para*80
                        pre = ovl + bpm_para*cvv.v_vel
                        ofs = rhy + bpm_para*500 - pre
                        con = pre + 50
                        cuf = - (con + 30)
                        numl_para = ",{:.1f},{:.1f},{:.1f},{:.1f}" \
                                    ",{:.1f}".format(ofs, con, cuf, pre, ovl)
                        if n > 1:
                            vr += "%s R" % n
                        else:
                            vr += " R"
                        vr_part.append(wav + vr + numl_para)

        self.oto.append(vc_part)
        self.oto.append(cv_part)
        self.oto.append(cv_head_part)
        self.oto.append(vr_part)

        # debug
        if debug:
            if gottal is None:
                gottal = set()
            if merge_cv:
                cv_num = len(self.cv_set)
            else:
                cv_num = len(self.cvv_set)
            if plan_b:
                cv_num *= 2
            if cv_head:
                if not merge_cv:
                    cv_head_num = len(self.cvv_set)
                else:
                    cv_head_num = len(self.cv_set)
            else:
                cv_head_num = 0
            vc_num = len(self.vr_set - gottal)*len(self.c_set)
            vr_num = len(self.vr_set)
            oto_num = cv_num + cv_head_num + vc_num + vr_num
            n = 0
            for oto_part in self.oto:
                n += len(oto_part)

            if (max_cv + max_vc + max_vr) == 3:
                if n != oto_num:
                    print("Warning: 实际oto数与预计oto数不符："
                          "{} != {}".format(n, oto_num))
                else:
                    print("实际oto数与预计oto数一致")
                    word_num = 0
                    for row in self.reclist:
                        for cvv in row:
                            if cvv.cvv == "R":
                                pass
                            word_num += 1
                    u = n / word_num
                    print("整音利用率为：{:.4f}（不含休止符R）".format(u))

                if vc_num != len(self.oto[0]):
                    print("Warning: vc部数目不符，"
                          "{} != {}".format(len(self.oto[0]), vc_num))
                if cv_num != len(self.oto[1]):
                    print("Warning: cv部数目不符，"
                          "{} != {}".format(len(self.oto[1]), cv_num))
                if cv_head_num != len(self.oto[2]):
                    print("Warning: 开头音部数目不符，"
                          "{} != {}".format(len(self.oto[2]), cv_head_num))
                if vr_num != len(self.oto[3]):
                    print("Warning: vr部数目不符，"
                          "{} != {}".format(len(self.oto[3]), vr_num))
            else:
                print("请注意：由于设置的最大相同oto数不全唯一，而且我很菜，所以只能保证oto总数"
                      "至少有一份的数量，只有不足时才会进行警告提示。")
                if n < oto_num:
                    print("Warning: 实际oto数与预计oto数不符："
                          "{} << {}".format(n, oto_num))
                else:
                    print("实际oto数至少含有一份的数量")
                    word_num = 0
                    for row in self.reclist:
                        for cvv in row:
                            if cvv.cvv == "R":
                                pass
                            word_num += 1
                    u = n / word_num
                    print("整音利用率为：{:.4f}（不含休止符R）".format(u))

    def output_list(self, reclist_name: str="reclist.txt", oto_name: str="oto.ini"):
        '''生成录音表和oto文件

        :param reclist_name: 录音表的文件名
        :param oto_name: oto的文件名
        :return: 将录音表和oto输出到当前文件目录
        '''
        # reclist
        reclist_str = ""
        for row in self.reclist:
            for cvv in row:
                reclist_str += "_%s" % cvv.cvv
            reclist_str += "\n"

        # oto
        oto_str = ""
        for oto_part in self.oto:
            for oto in oto_part:
                oto_str += "%s\n" % oto

        # output files
        with open(reclist_name, mode="w+") as f:
            f.write(reclist_str)

        with open(oto_name, mode="w+") as f:
            f.write(oto_str)
