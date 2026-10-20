using Godot;
using System;

public partial class FollowCam : Camera2D
{
	[Export]
	public Node2D Target;
	
	[Export]
	public float XDistance;
	
	[Export]
	public float YDistance;
	
	public override void _PhysicsProcess(double delta)
	{
		if(Target == null || Target == this)
			return;
			
		Position = Target.Position + new Vector2(XDistance, YDistance);
	}
}
