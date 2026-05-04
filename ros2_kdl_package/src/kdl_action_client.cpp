#include <chrono>
#include <cstdlib>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "ros2_kdl_package/action/kdl_trajectory.hpp"

using namespace std::chrono_literals;
using KDLTrajectory = ros2_kdl_package::action::KDLTrajectory;
using GoalHandleKDLTrajectory = rclcpp_action::ClientGoalHandle<KDLTrajectory>;

class KDLActionClient : public rclcpp::Node
{
public:
  KDLActionClient() : Node("kdl_action_client")
  {
    client_ = rclcpp_action::create_client<KDLTrajectory>(
      this,
      "execute_kdl_trajectory"
    );
  }

  void send_goal()
  {
    if (!client_->wait_for_action_server(10s))
    {
      RCLCPP_ERROR(get_logger(), "Action server not available.");
      rclcpp::shutdown();
      return;
    }

    auto goal_msg = KDLTrajectory::Goal();
    goal_msg.start = true;

    RCLCPP_INFO(get_logger(), "Sending KDL trajectory action goal.");

    auto send_goal_options = rclcpp_action::Client<KDLTrajectory>::SendGoalOptions();

    send_goal_options.goal_response_callback =
      [this](const GoalHandleKDLTrajectory::SharedPtr & goal_handle)
      {
        if (!goal_handle)
        {
          RCLCPP_ERROR(this->get_logger(), "Goal was rejected.");
        }
        else
        {
          RCLCPP_INFO(this->get_logger(), "Goal accepted.");
        }
      };

    send_goal_options.feedback_callback =
      [this](
        GoalHandleKDLTrajectory::SharedPtr,
        const std::shared_ptr<const KDLTrajectory::Feedback> feedback)
      {
        RCLCPP_INFO(
          this->get_logger(),
          "Feedback: time=%.3f s, error_norm=%.6f m",
          feedback->time,
          feedback->error_norm
        );
      };

    send_goal_options.result_callback =
      [this](const GoalHandleKDLTrajectory::WrappedResult & result)
      {
        switch (result.code)
        {
          case rclcpp_action::ResultCode::SUCCEEDED:
            RCLCPP_INFO(
              this->get_logger(),
              "Action succeeded: %s",
              result.result->message.c_str()
            );
            break;
          case rclcpp_action::ResultCode::ABORTED:
            RCLCPP_ERROR(this->get_logger(), "Action aborted.");
            break;
          case rclcpp_action::ResultCode::CANCELED:
            RCLCPP_WARN(this->get_logger(), "Action canceled.");
            break;
          default:
            RCLCPP_ERROR(this->get_logger(), "Unknown result code.");
            break;
        }

        rclcpp::shutdown();
      };

    client_->async_send_goal(goal_msg, send_goal_options);
  }

private:
  rclcpp_action::Client<KDLTrajectory>::SharedPtr client_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<KDLActionClient>();
  node->send_goal();
  rclcpp::spin(node);
  return 0;
}
