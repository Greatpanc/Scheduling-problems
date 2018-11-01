import numpy as np
import copy
"""
datasets=[] #datasets[i,j,k],i取活动编号,j代表：0——通常模式,k代表:1——R1
            #                                 1——压缩模式       2——R2
            #                                                  3——R3
            #                                                  4——工期

eventlist=[]    #event[i]代表为第i个事件节点,EventNode对象数组

activitylist #activitylist[i,j],i取活动编号,j代表:0——该活动的前置事件
                                                1——该活动的后置事件

event2activity #event2activity[i,j] i取前置事件id号,j取后置事件id号,其值为对应的活动号
"""

"""
    事件类：属性 —— its_id :事件的id号
                   tc：时间约束，说明完成该事件开始时间必须大于该值
                   predev[i]:紧前事件集合
                   nextdev[i][j]:j=0第i个紧后事件对应的id号,j=1是执行该事件所对应的活动
"""
class EventNode:
    def __init__(self,its_id=0):
        self.its_id =its_id
        self.tc=0               #时间约束
        self.predev =[]
        self.nextdev=[]

"""
	函数名：getData()
	函数功能：	从外界读取项目数据并处理
		输入	无
		输出	1 datasets：datasets[i,j,k]，不同模式下各活动的具体参数矩阵，具体说明见数据说明部分
			2 eventlist：事件对象列表，eventlist[event_id]代表event_id事件的对象
			3 activitylist：activitylist[i,j]记录i活动的前后置事件的事件号，具体说明见数据说明部分
            4 activity_num：总活动数
            5 event_num：总事件数
            6 event2activity：event2activity[i,j],通过前(i)后(j)置事件id号索取活动编号矩阵
            7 R：R[i],i资源的总量
	其他说明：无
"""
def getData():
    datafile=open("data.txt")
    dataflame=datafile.read()
    datafile.close()

    data_temp=dataflame.split("\n")
    event_num=int(data_temp[0].split("%*%")[0])+2
    activity_num=int(data_temp[0].split("%*%")[1])+2
    R=[]
    R.append(int(data_temp[0].split("%*%")[2])+1)
    R.append(int(data_temp[0].split("%*%")[3])+1)
    R.append(int(data_temp[0].split("%*%")[4])+1)
    eventlist=construct_graph(event_num)

    datasets=np.zeros((activity_num,2,4),dtype=np.int)
    activitylist=np.zeros((activity_num,2),dtype=np.int)
    event2activity=np.zeros((activity_num,activity_num),dtype=np.int)

    for temp in data_temp[2:]:
        data=temp.split("/")
        data1=data[0].split(" ")

        i=int(data1[0])
        datasets[i,0,0]=int(data1[1])   # 工期
        datasets[i,0,1]=int(data1[2])   # R1资源
        datasets[i,0,2]=int(data1[3])   # R2资源
        datasets[i,0,3]=int(data1[4])   # R3资源
        datasets[i,1,0]=int(data1[5])   # 工期
        datasets[i,1,1]=int(data1[6])   # R1资源
        datasets[i,1,2]=int(data1[7])   # R2资源
        datasets[i,1,3]=int(data1[8])   # R3资源

        data2=data[1].split("-")
        cur_node=int(data2[0])
        next_node=int(data2[1])
        eventlist[cur_node].nextdev.append([next_node,i])
        eventlist[next_node].predev.append(cur_node)
        event2activity[cur_node,next_node]=i
        activitylist[i,0]=cur_node
        activitylist[i,1]=next_node
    return datasets,eventlist,activitylist,activity_num,event_num,event2activity,R

"""
	函数名：get_etatable(activity_num)
	函数功能：	根据总活动数初始化启发项矩阵
		输入	1 activity_num：总活动数
		输出	1 etatable：启发项矩阵,etatable[i,j]代表i活动j模式(j=0-正常模式,j=1-压缩模式)的启发值
	其他说明：无
"""
def get_etatable(activity_num):
    etatable=np.zeros([activity_num,2])
    for i in range(activity_num):
        etatable[i,0]=(datasets[i,0,1]+datasets[i,0,2]+datasets[i,0,3])/(R[0]+R[1]+R[2])
        etatable[i,1]=(datasets[i,1,1]+datasets[i,1,2]+datasets[i,1,3])/(R[0]+R[1]+R[2])
    return etatable


"""
	函数名：init_pheromonetable(activity_num)
	函数功能：	根据总活动数初始化信息素矩阵
		输入	1 activity_num：总活动数
		输出	1 pheromonetable：信息素矩阵,pheromonetable[i,j]代表
                    i活动j模式(j=0-正常模式,j=1-压缩模式)的信息素含量
	其他说明：无
"""
def init_pheromonetable(activity_num):
    pheromonetable=np.ones((activity_num,2))*Q/activity_num
    return pheromonetable

"""
	函数名：construct_graph(event_num)
	函数功能：	根据事件总数生成对象列表
		输入	1 event_num：总事件数
		输出	1 eventlist：事件对象列表，eventlist[event_id]代表event_id事件的对象

	其他说明：无
"""
def construct_graph(event_num):
    eventlist=[]
    for i in range(event_num):
        eventnode=EventNode(i)
        eventlist.append(eventnode)
    return eventlist


"""
	函数名：check_predev(eventnode)
	函数功能：	检测是否有紧前事件
		输入	1 eventnode：事件对象
		输出	1 True:有紧前事件
              False：无紧前事件
	其他说明：无
"""
def check_predev(eventnode):
    return True if eventnode.predev else False

"""
	函数名：check_nextdev(eventnode)
	函数功能：	检测是否有紧后事件
		输入	1 eventnode：事件对象
		输出	1 True:有紧后事件
              False：无紧后事件
	其他说明：无
"""
def check_nextdev(eventnode):
    return True if eventnode.nextdev else False

"""
	函数名：check_finish(eventlist_finish)
	函数功能：	检查是不是所有事件（不包括结束虚事件）都完成
		输入	1 eventlist_finish：当前完成的活动列表
		输出	1 True:是
              False：否
	其他说明：无
"""
def check_finish(eventlist_finish):
    for i in range(event_num-2):
        if i not in eventlist_finish:
            return False
    if event_num-2 in eventlist_finish:
        return False
    return True

"""
	函数名：parameters_init()
	函数功能： 蚂蚁开始走的过程中的参数初始化函数
		输入	1 无
		输出	1 无
	其他说明：   对当前事件cur_time=0,
                R1当前资源量=R1资源总量
                R2当前资源量=R2资源总量
                R3当前资源量=R3资源总量
"""
def parameters_init():
    cur_time=0
    res_time=[]

    eventlist_finish=[]
    eventlist_finish.append(0)

    activity_waited=[]
    activity_waited.append(0)

    activitylist_finish=[]

    R1=R[0]
    R2=R[1]
    R3=R[2]

    return cur_time,res_time,eventlist_finish,\
        activity_waited,activitylist_finish,R1,R2,R3

"""
	函数名： timeseries_constraint(next_eventnode)
	函数功能： 时序约束,当前活动的开始时间应该要满足后续事件能够执行的最早时间
            函数执行完后当前时间满足了资源约束
        输入	1 activity：活动id号
	其他说明：无
"""
def timeseries_constraint(activity):
    next_eventnode=activitylist[activity,1]
    global cur_time
    if eventlist[next_eventnode].tc>cur_time:
        cur_time=eventlist[next_eventnode].tc
        time_ahead(cur_time)

"""
	函数名：resource_constraint(activity,mode)
	函数功能： 当前活动的开始时间应该要满足当前资源能够支持其执行,
            函数执行完后当前时间满足了资源约束
        输入	1 activity：活动id号
        输入	2 mode:模式类型,mode=0代表通常模式,mode=1代表压缩模式
	其他说明：   对当前事件cur_time=0,
                R1当前资源量=R1资源总量
                R2当前资源量=R2资源总量
                R3当前资源量=R3资源总量
"""
def resource_constraint(activity,mode):
    global R1,R2,R3,cur_time
    while True:
        if(R1>=datasets[activity,mode,1] and R2>=datasets[activity,mode,2] and R3>=datasets[activity,mode,3]):
            R1-=datasets[activity,mode,1]
            R2-=datasets[activity,mode,2]
            R3-=datasets[activity,mode,3]
            break
        elif res_time:
            cur_time=min([i[0] for i in res_time])
            time_ahead(cur_time)
        else:
            print([R1,R2,R3,activity])
            exit()

"""
	函数名：update_list(activity,mode)
	函数功能： 更新活动列表和已完成时间列表信息,
        输入	1 activity：活动id号
        输入	2 mode:模式类型,mode=0代表通常模式,mode=1代表压缩模式
	其他说明： 无
"""
def update_list(activity,mode):
    next_eventnode=activitylist[activity,1]

    activity_waited.remove(activity)
    res_time.append([cur_time+datasets[activity,mode,0],activity,mode])
    if len(activity_waited)==0 and check_finish(eventlist_finish):
        eventlist_finish.append(event_num-2)
        activity_waited.append(activity_num-1)
    elif next_eventnode!=event_num-2 and next_eventnode not in eventlist_finish:
        eventlist_finish.append(next_eventnode)
        for event in eventlist[next_eventnode].nextdev:
            eventnode=eventlist[event[0]]
            flag=True
            for i in eventnode.predev:
                    if i not in eventlist_finish:
                        flag=False
            if flag:
                for i in eventnode.predev:
                    activity_waited.append(event2activity[i,eventnode.its_id])
    
    activitylist_finish.append([activity,mode,cur_time])

"""
	函数名：go_a_step(activity,mode)
	函数功能： 蚂蚁按活动activity的模式mode行进一步
		输入	1 activity：活动id号
        输入	2 mode:模式类型,mode=0代表通常模式,mode=1代表压缩模式
		输出	1 无
	其他说明：   时序约束部分：当前活动的开始时间应该要满足后续事件能够执行的最早时间
                资源约束部分：当前活动的开始时间应该要满足当前资源能够支持其执行
                更新事件过程：当前活动执行完后,在当前活动等待列列表中删去该活动,
                    并把符合约束的后续活动加入到当前活动等待列表中
                
"""
def go_a_step(activity,mode):
    global R1,R2,R3,cur_time

    if activity==activity_num-1:
        cur_time=min([i[0] for i in res_time])
        eventlist_finish.append(event_num-1)
        activitylist_finish.append([activity,mode,cur_time])
    else:
        #时序约束,执行后当前时间满足时序约束
        timeseries_constraint(activity)

        #资源约束,执行后当前时间满足资源约束
        resource_constraint(activity,mode)

        #更新活动列表和已完成时间列表信息
        update_list(activity,mode)

"""
	函数名：time_ahead(time)
	函数功能：	删去当前资源时间结束列表中时间小于time的项，并更新当前资源量
		输入	1 time：当前时间
		输出	1 无
	其他说明：无
"""
def time_ahead(time):
    global R1,R2,R3
    for res in res_time:
        if res[0]<=time:
            R1+=datasets[res[1],res[2],1]
            R2+=datasets[res[1],res[2],2]
            R3+=datasets[res[1],res[2],3]
            res_time.remove(res)

##############################程序入口#########################################
if __name__=="__main__":
    datasets,eventlist,activitylist,activity_num,event_num,event2activity,R=getData()

    ant_num = 10                    # 蚂蚁个数
    alpha = 0.1                     # 信息素重要程度因子
    beta = 1                        # 启发函数重要程度因子
    rho = 0.2                       # 信息素的挥发速度
    Q = 1                           # 品质因子
    itermax = 1000                   # 最大迭代次数

    etatable = get_etatable(activity_num)      # 初始化启发函数矩阵
    pheromonetable=init_pheromonetable(activity_num)   # 初始化信息素矩阵

    result_record=[]                # 各代蚂蚁行走结果记录矩阵
    aver_time = np.zeros(itermax)   # 各代路径的平均时间
    time_best = np.zeros(itermax)   # 各代及其之前遇到的最佳时间
    activitylist_best = np.zeros((itermax,activity_num,3),dtype="int") # 各代及其之前遇到的最佳路径时间

    iter = 0
    # 从0代开始进行让蚂蚁在AOA图上进行搜索
    while iter < itermax:
        activitylist_result=[]      # 记录当前代各蚂蚁所探求的解

        # 依次让各只蚂蚁寻求一组解
        for i in range(0,ant_num): 
            # 初始化蚂蚁探求解的各个参数
            cur_time,res_time,\
                eventlist_finish,activity_waited,activitylist_finish,\
                    R1,R2,R3=parameters_init()

            # 每次用轮盘法选择下一个要执行的活动,直到所有活动都被执行完毕
            for j in range(0,activity_num):      
                if len(activity_waited)==1:     
                    go_a_step(activity_waited[0],0)
                else:
                    probtrans = np.zeros(2*len(activity_waited))
                    for k in range(len(activity_waited)):
                        probtrans[2*k] = np.power(pheromonetable[k][0],alpha)\
                                *np.power(etatable[k][0],alpha)
                        probtrans[2*k+1] = np.power(pheromonetable[k][1],alpha)\
                                *np.power(etatable[k][1],alpha)
                    cumsumprobtrans = (probtrans/sum(probtrans)).cumsum()
                    cumsumprobtrans -= np.random.rand()
                    k = np.where(cumsumprobtrans>0)[0][0]    # 下一个活动
                    pheromonetable[activity_waited[int(k/2)],k%2]=\
                        (1-rho)*pheromonetable[activity_waited[int(k/2)],k%2]+rho*Q/activity_num
                    go_a_step(activity_waited[int(k/2)],k%2)

            # 将该只蚂蚁探求的结果保存
            activitylist_result.append(activitylist_finish)

        # 对该代蚂蚁的最佳值与当前最佳值进行比较并更新当前最佳值及路径
        activitylist_result=np.array(activitylist_result)
        aver_time[iter] = activitylist_result[:,-1,2].mean()
        if iter == 0:
            time_best[iter] = activitylist_result[:,-1,2].min()
            activitylist_best[iter] = activitylist_result[activitylist_result[:,-1,2].argmin()].copy()      
        else:
            if activitylist_result[:,-1,2].min() > time_best[iter-1]:
                time_best[iter] = time_best[iter-1]
                activitylist_best[iter] = activitylist_best[iter-1].copy()
            else:
                time_best[iter] = activitylist_result[:,-1,2].min()
                activitylist_best[iter] = activitylist_result[activitylist_result[:,-1,2].argmin()].copy()  

        # 将该代蚂蚁所探求的所有解保存下来
        result_record.append(activitylist_result)

        # 更新信息素
        changepheromonetable = np.zeros((activity_num,2))
        for j in range(activity_num-1):
            activity=activitylist_best[iter][j,0]
            mode=activitylist_best[iter][j,1]
            time=activitylist_best[iter][j,2]
            changepheromonetable[activity,mode]+=Q/activitylist_best[iter][-1,2]
        pheromonetable = pheromonetable + changepheromonetable

        # 将蚂蚁增加一代
        iter+=1

    # 结果输出
    print(time_best[itermax-1])
    print(activitylist_best[itermax-1])

