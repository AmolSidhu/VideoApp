import React, { Component } from "react";
import { Form, Button, Alert, Badge, ProgressBar } from "react-bootstrap";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import server from "../static/Constants";

class BatchVideoUploadForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      videos: [],
      thumbnail: null,
      private: false,
      permission: "",
      existing_series: false,
      errorMessage: "",
      message: [],
      progress: 0,
      customTag: "",
      tags: ["action", "comedy", "drama", "horror", "thriller", "adventure"],
      action: false,
      comedy: false,
      drama: false,
      horror: false,
      thriller: false,
      description: "",
      imdbLink: "",
      directors: [],
      stars: [],
      writers: [],
      creators: [],
      criticRating: "",
      title: "",
      season: 1,
    };
  }

  handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    this.setState({
      [name]: type === "checkbox" ? checked : value,
    });
  };

  handleFileChange = (event) => {
    this.setState({
      videos: Array.from(event.target.files),
    });
  };

  handleImageChange = (event) => {
    this.setState({
      thumbnail: event.target.files[0],
    });
  };

  handleTagClick = (tag) => {
    this.setState(
      (prevState) => ({
        [tag]: !prevState[tag],
      }),
      () => {
        console.log(
          `Clicked ${tag}, variant: ${
            this.state[tag] ? "primary" : "secondary"
          }`
        );
      }
    );
  };

  handleCustomTagChange = (event) => {
    this.setState({
      customTag: event.target.value,
    });
  };

  handleAddCustomTag = () => {
    const { customTag, tags } = this.state;

    if (customTag && !tags.includes(customTag)) {
      this.setState((prevState) => ({
        tags: [...prevState.tags, customTag],
        [customTag]: true,
        customTag: "",
      }));
    }
  };

  handleDragEnd = (result) => {
    if (!result.destination) return;

    const videos = Array.from(this.state.videos);
    const [reorderedVideo] = videos.splice(result.source.index, 1);
    videos.splice(result.destination.index, 0, reorderedVideo);

    this.setState({
      videos,
    });
  };

  handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    this.state.videos.forEach((video) => {
      formData.append("videos", video);
    });
    if (this.state.thumbnail) {
      formData.append("thumbnail", this.state.thumbnail);
    }
    formData.append(
      "tags",
      JSON.stringify(this.state.tags.filter((tag) => this.state[tag]))
    );
    formData.append("private", this.state.private);
    formData.append("permission", this.state.permission);
    formData.append("existing_series", this.state.existing_series);
    formData.append("description", this.state.description);
    formData.append("imdbLink", this.state.imdbLink);
    formData.append("directors", JSON.stringify(this.state.directors));
    formData.append("stars", JSON.stringify(this.state.stars));
    formData.append("writers", JSON.stringify(this.state.writers));
    formData.append("creators", JSON.stringify(this.state.creators));
    formData.append("criticRating", this.state.criticRating);
    formData.append("title", this.state.title);
    formData.append("season", this.state.season);

    const token = localStorage.getItem("token");
    const url = `${server}/upload/batch/`;

    const config = {
      method: "PATCH",
      headers: {
        Authorization: token,
      },
      body: formData,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error("An error occurred while uploading the videos.");
      }

      const responseData = await response.json();
      this.setState({ message: responseData.responses });
    } catch (error) {
      this.setState({ errorMessage: error.message });
    }
  };

  render() {
    const { tags, customTag, videos, message } = this.state;

    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Group>
          <Form.Label>Videos</Form.Label>
          <Form.Control
            type="file"
            multiple
            accept="video/*"
            onChange={this.handleFileChange}
          />
        </Form.Group>
        <DragDropContext onDragEnd={this.handleDragEnd}>
          <Droppable droppableId="videos">
            {(provided) => (
              <div {...provided.droppableProps} ref={provided.innerRef}>
                {videos.map((video, index) => (
                  <Draggable key={video.name} draggableId={video.name} index={index}>
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        style={{
                          userSelect: "none",
                          padding: 16,
                          margin: "0 0 8px 0",
                          minHeight: "50px",
                          backgroundColor: "#fff",
                          color: "#000",
                          ...provided.draggableProps.style,
                        }}
                      >
                        {video.name}
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
        <Form.Group>
          <Form.Label>Thumbnail</Form.Label>
          <Form.Control
            type="file"
            accept="image/*"
            onChange={this.handleImageChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Tags</Form.Label>
          <div>
            {tags.map((tag) => (
              <Badge
                key={tag}
                pill
                variant={this.state[tag] ? "primary" : "secondary"}
                onClick={() => this.handleTagClick(tag)}
                style={{ cursor: "pointer", marginRight: "5px" }}
              >
                {tag}
              </Badge>
            ))}
          </div>
          <Form.Control
            type="text"
            placeholder="Custom tag"
            value={customTag}
            onChange={this.handleCustomTagChange}
            onKeyPress={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                this.handleAddCustomTag();
              }
            }}
          />
          <Button variant="outline-secondary" onClick={this.handleAddCustomTag}>
            Add
          </Button>
        </Form.Group>
        <Form.Group>
          <Form.Label>Description</Form.Label>
          <Form.Control
            type="text"
            name="description"
            value={this.state.description}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>IMDb Link</Form.Label>
          <Form.Control
            type="text"
            name="imdbLink"
            value={this.state.imdbLink}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Directors</Form.Label>
          <Form.Control
            type="text"
            name="directors"
            value={this.state.directors}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Stars</Form.Label>
          <Form.Control
            type="text"
            name="stars"
            value={this.state.stars}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Writers</Form.Label>
          <Form.Control
            type="text"
            name="writers"
            value={this.state.writers}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Creators</Form.Label>
          <Form.Control
            type="text"
            name="creators"
            value={this.state.creators}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Critic Rating</Form.Label>
          <Form.Control
            type="text"
            name="criticRating"
            value={this.state.criticRating}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Title</Form.Label>
          <Form.Control
            type="text"
            name="title"
            value={this.state.title}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Season</Form.Label>
          <Form.Control
            type="number"
            name="season"
            value={this.state.season}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Check
            type="checkbox"
            label="Private"
            name="private"
            checked={this.state.private}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Label>Permission</Form.Label>
          <Form.Control
            type="text"
            name="permission"
            value={this.state.permission}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        <Form.Group>
          <Form.Check
            type="checkbox"
            label="Existing Series"
            name="existing_series"
            checked={this.state.existing_series}
            onChange={this.handleInputChange}
          />
        </Form.Group>
        {this.state.errorMessage && (
          <Alert variant="danger">{this.state.errorMessage}</Alert>
        )}
        {message && (
          <Alert variant="success">
            {message.map((msg, index) => (
              <div key={index}>
                {msg.video_name}: {msg.message}
              </div>
            ))}
          </Alert>
        )}
        <Button variant="primary" type="submit">
          Upload Videos
        </Button>

        {this.state.progress > 0 && (
          <ProgressBar
            striped
            variant="success"
            now={this.state.progress}
            label={`${this.state.progress}%`}
          />
        )}
      </Form>
    );
  }
}

export default BatchVideoUploadForm;
