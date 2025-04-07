from graphviz import Digraph

# 创建有向图
dot = Digraph(comment='Enhanced Dialogue Management Flow', format='svg')
dot.attr(rankdir='TB', splines='ortho', nodesep='1.2')

# 定义公共样式
node_style = {'shape': 'rectangle', 'style': 'rounded,filled', 'fillcolor': '#E8F5E9', 'fontname': 'Arial'}
cond_style = {'shape': 'diamond', 'style': 'filled', 'fillcolor': '#FFF3E0', 'fontname': 'Arial'}
memory_style = {'shape': 'cylinder', 'style': 'filled', 'fillcolor': '#E1F5FE'}

# Memory存取说明子图
with dot.subgraph(name='cluster_memory') as mem:
    mem.attr(label='Memory Architecture', style='dashed')
    mem.node('wm', 'Working Memory\n(RAM)\n- Current session context\n- Emotion analysis results\n- Dialogue state',
             **memory_style)
    mem.node('sm',
             'Semantic Memory\n(PubMed Psychology Abstracts)\n- Psychological knowledge base\n- Therapy techniques\n- Case studies',
             **memory_style)
    mem.node('em', 'Episodic Memory\n(MongoDB)\n- User profiles\n- Historical emotion data\n- Dialogue records',
             **memory_style)

# 主流程
with dot.subgraph(name='cluster_main') as main:
    # 用户身份验证
    main.node('start', 'User Access Point', **node_style)
    main.node('auth', 'Login/Registration\n(Verify with MongoDB)', **node_style)
    main.node('load_data', 'Load User Data\n(Episodic Memory)', **node_style)

    # 输入处理
    main.node('multi_input',
              'Multi-modal Input\n1. Voice (Wav2Vec transcription)\n2. Text input\n3. Facial expression (DeepFace)',
              **node_style)

    # 情感分析
    main.node('emotion_analysis', '''Multi-source Emotion Analysis:
1. Voice sentiment (audio waveform)
2. Text sentiment (transcript)
3. Facial expression''', **node_style)

    main.node('consistency_check', 'Emotion Consistency Check\n(3-way comparison)', **cond_style)
    main.node('handle_conflict', 'Resolve Emotion Conflicts\n(Store in Episodic Memory)', **node_style)

    # 心理辅导流程
    main.node('therapy', 'Psychological Support Flow', **node_style)
    # main.node('update_wm', 'Update Working Memory\n(Current emotion state)', **node_style)

# 心理辅导子流程
with dot.subgraph(name='cluster_therapy') as th:
    th.attr(label='Psychological Support Flow', style='dashed')
    th.node('retrieve', 'Retrieve from:\n- Semantic Memory (PubMed)\n- Episodic Memory (User history)', **node_style)
    th.node('generate', 'Generate Response\n(LangChain + OpenAI)', **node_style)
    th.node('decide', 'Continue Dialogue?', **cond_style)

# 修复连接边 - 使用单独的edge()调用代替edges()
dot.edge('start', 'auth')
dot.edge('auth', 'load_data')
dot.edge('load_data', 'multi_input')
dot.edge('multi_input', 'emotion_analysis')
dot.edge('emotion_analysis', 'consistency_check')
dot.edge('consistency_check', 'handle_conflict', label='Inconsistent')
dot.edge('consistency_check', 'therapy', label='Consistent')
dot.edge('handle_conflict', 'therapy')
# dot.edge('therapy', 'retrieve')
dot.edge('retrieve', 'generate')
dot.edge('generate', 'decide')
dot.edge('decide', 'multi_input', label='Yes')
# dot.edge('decide', 'update_wm', label='No')
# dot.edge('update_wm', 'em')

# 内存交互
dot.edge('emotion_analysis', 'wm', label='Store temp results', style='dashed')
dot.edge('retrieve', 'sm', label='Knowledge query', style='dashed')
dot.edge('retrieve', 'em', label='History query', style='dashed')
dot.edge('handle_conflict', 'em', label='Persist conflict', style='dashed')

# 修复拼写错误
dot.subgraph(name='cluster_memory')  # 修正cluster_memory拼写

dot.render('enhanced_flow', view=True, format="svg")