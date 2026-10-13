using Godot;
using System;

public partial class MainMenu : Control
{
	public void play(){
		GetTree().ChangeSceneToFile("uid://cuuimd7fyr2kj");
	}
	
	public void keyboard(){
		//Change mode in singleton
		play();
	}
	
	public void vocal(){
		//Change mode in singleton
		//Start Python process
		play();
	}
	
	public void sound(){
		//Change mode in singleton
		//Start python process
		play();
	}
}
