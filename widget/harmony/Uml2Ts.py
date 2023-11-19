from util.StrUtil import StrUtil

uml = """
@startuml
hide empty description
state A #green
state B #green
state C #green
state D #green
state FAILED #green
[*] --> init
init --> check
check --> C
C --> D
D --> E
D --> Failed
C --> Failed
check --> Failed
init --> Failed
@enduml
"""

if __name__ == '__main__':
    lines = uml.split('\n')
    nodeLines = [item for item in lines if '-->' in item]
    print(nodeLines)
    tree = {}
    tasks = []
    for item in nodeLines:
        nodes = item.split('-->')
        if '[*]' in nodes[0]:
            tree['root'] = StrUtil.under2camel(nodes[1].strip())
            tasks.append(tree['root'])
        else:
            parentNode = StrUtil.under2camel(nodes[0].strip())
            childNode = StrUtil.under2camel(nodes[1].strip())
            if parentNode not in tasks:
                tasks.append(parentNode)
            if childNode not in tasks:
                tasks.append(childNode)
            if parentNode in tree:
                tree[parentNode].append(childNode)
            else:
                tree[parentNode] = []
                tree[parentNode].append(childNode)
    print(tree)
    print(tasks)
    taskEnum = ''

    for index, task in enumerate(tasks):
        sp = "" if index == 0 else ",\n"
        taskEnum += f'{sp}  {StrUtil.camel2under(task)} = "{task}"'
    print('Tasks:')
    print("export const enum Tasks {\n" + taskEnum + "\n}")

    print('Build tree:')
    print('  private buildTree() {\n    let builder = new DecisionTreeBuilder<Tasks, TreeContext>();')

    root = tree['root']
    for key, childNodes in tree.items():
        if key == 'root':
            continue
        print(f'    builder.{"root" if key == root else "node"}(Tasks.{StrUtil.camel2under(key)}, async (ctx?: TreeContext) => {{\n      return this.{key}Action();\n    }}')
        for childNode in childNodes:
            isLeaf = False if childNode in tree else True
            funcContent = f"this.{childNode}Action();" if isLeaf else f"return this.{childNode}Action();"
            print(f'    {".leaf" if isLeaf else ".nonLeaf"}(Tasks.{StrUtil.camel2under(childNode)}, async (ctx?: TreeContext) => {{\n      {funcContent}\n    }}')
        print()
    print('    this.tree = builder.build();\n  }')

    for task in tasks:
        print(f'\n  async {task}Action(){{\n  }}')

