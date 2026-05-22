#include "kdl_control.h"

#include <algorithm>
#include <cmath>

KDLController::KDLController(KDLRobot &_robot)
{
    robot_ = &_robot;
}

Eigen::VectorXd KDLController::idCntr(KDL::JntArray &_qd,
                                      KDL::JntArray &_dqd,
                                      KDL::JntArray &_ddqd,
                                      double _Kp, double _Kd)
{
    // read current state
    Eigen::VectorXd q = robot_->getJntValues();
    Eigen::VectorXd dq = robot_->getJntVelocities();

    // calculate errors
    Eigen::VectorXd e = _qd.data - q;
    Eigen::VectorXd de = _dqd.data - dq;

    Eigen::VectorXd ddqd = _ddqd.data;
    return robot_->getJsim() * (ddqd + _Kd*de + _Kp*e)
            + robot_->getCoriolis() + robot_->getGravity();
}

Eigen::VectorXd KDLController::idCntr(KDL::Frame &_desPos,
                                      KDL::Twist &_desVel,
                                      KDL::Twist &_desAcc,
                                      double _Kpp, double _Kpo,
                                      double _Kdp, double _Kdo)
{
    (void)_desPos;
    (void)_desVel;
    (void)_desAcc;
    (void)_Kpp;
    (void)_Kpo;
    (void)_Kdp;
    (void)_Kdo;

    return Eigen::VectorXd::Zero(robot_->getNrJnts());
}

Eigen::VectorXd KDLController::velocity_ctrl_null(const Eigen::Vector3d &_desVel,
                                                  const Eigen::Vector3d &_posError,
                                                  double _Kp,
                                                  double _lambda)
{
    const unsigned int nj = robot_->getNrJnts();

    Eigen::MatrixXd J_full = robot_->getEEJacobian().data;
    Eigen::MatrixXd J = J_full.topRows(3);

    Eigen::MatrixXd J_pinv = pseudoinverse(J);

    Eigen::Vector3d xdot_des = _desVel + _Kp * _posError;
    Eigen::VectorXd qdot_task = J_pinv * xdot_des;

    Eigen::VectorXd q = robot_->getJntValues();
    Eigen::VectorXd qdot0 = Eigen::VectorXd::Zero(nj);

    Eigen::VectorXd q_min(nj);
    Eigen::VectorXd q_max(nj);

    q_min << -2.96, -2.09, -2.96, -2.09, -2.96, -2.09, -2.96;
    q_max <<  2.96,  2.09,  2.96,  2.09,  2.96,  2.09,  2.96;

    for (unsigned int i = 0; i < nj; ++i)
    {
        const double range = q_max(i) - q_min(i);
        const double upper_dist = std::max(q_max(i) - q(i), 1e-3);
        const double lower_dist = std::max(q(i) - q_min(i), 1e-3);

        const double denom = std::pow(upper_dist, 2.0) * std::pow(lower_dist, 2.0);

        // Negative gradient of the joint-limit barrier function.
        // This pushes joints away from their limits.
        double grad = (std::pow(range, 2.0) / _lambda) *
                      ((2.0 * q(i) - q_max(i) - q_min(i)) / denom);

        qdot0(i) = std::clamp(-grad, -0.05, 0.05);
    }

    Eigen::MatrixXd I = Eigen::MatrixXd::Identity(nj, nj);
    Eigen::MatrixXd N = I - J_pinv * J;

    Eigen::VectorXd qdot = qdot_task + N * qdot0;

    return qdot;
}
