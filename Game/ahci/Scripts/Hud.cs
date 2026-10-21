using Godot;
using System;

public partial class Hud : Control
{
	[Export] public Label[] Controls;
	
	public override void _Ready()
	{
		Reveal(GameMaster.Instance.Book);
	}
	
	public void Reveal(int Book)
	{
		GD.Print(Book);
		for(int i = 0; i < Book+1; i++)
		{
			Controls[i].Show();
		}
	}
}
