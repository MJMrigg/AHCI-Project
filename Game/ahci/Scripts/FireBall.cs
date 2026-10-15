using Godot;
using System;

public partial class FireBall : CharacterBody2D
{
	[Export]
	private float _speed;

	public override void _PhysicsProcess(double delta)
	{
		base._PhysicsProcess(delta);
		// GD.Print(Rotation);

		Velocity = Transform.X.Normalized() * _speed;

		MoveAndSlide();
	}

	private void OnBodyEntered(Node2D body)
	{
		// when fireball hits a body

		// TODO: if fireball hits wood then destroy it

		CallDeferred(MethodName.QueueFree);
	}
}
