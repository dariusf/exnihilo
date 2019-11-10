
def choice(choices):
  while True:
    # TODO map some other letters?
    for i, choice in enumerate(choices):
      print(f'{i+1}. {choice}')
    inp = input('? ')
    try:
      inp = int(inp)
      if inp <= 0 or inp > len(choices):
        print('Invalid choice\n')
      else:
        return choices[inp-1]
    except ValueError:
      print('Invalid choice\n')
