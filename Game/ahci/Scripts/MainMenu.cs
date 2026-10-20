using Godot;
using System;
using System.Diagnostics;

public partial class MainMenu : Control
{
	
	public void Keyboard(){
		GameMaster.Instance.StartKeyboard();
	}
	
	public void Vocal(){
		GameMaster.Instance.StartVocal();
	}
	
	public void Sound(){
		GameMaster.Instance.StartSound();
	}
}
